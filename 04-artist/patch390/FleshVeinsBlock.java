package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.infection.VeinMutationEngine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.MultifaceSpreader;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

/**
 * Плотоные жилы на гранях блоков — от тонкой t1 до почти поглотившей блок t4.
 *
 * <p><b>Почему тир — состояние, а не четыре блока.</b> Жила одного тира
 * превращается в соседний тир на месте, сохраняя грани и вариацию. Четыре
 * отдельных блока потребовали бы переносить свойства при каждой мутации и
 * держать четыре реестровых записи ради одного и того же поведения.
 *
 * <p><b>Вариация.</b> У каждого тира три рисунка ({@code VARIANT} 0..2),
 * выбираются один раз при установке и дальше не меняются: жила растёт, но
 * остаётся собой. Иначе соседние жилы перерисовывались бы на каждом тике
 * роста, и улей «мерцал» бы.
 *
 * <p><b>Зачем тиры.</b> Жила — след заражения: {@code flesh_block} заражает
 * соседа, на его гранях появляется t1. Дочерняя жила выросла на блок дальше —
 * родитель поднимается на тир (каскад до t4). Обратный ход: дочерние жилы
 * отсечены, значит источник «не дотягивается» — тир падает, а на нуле жила
 * исчезает. Жила t4, у которой появился свой росток, поглощает блок:
 * {@code flesh_block} вместо жилы. Это и есть «t5».
 */
public final class FleshVeinsBlock extends MultifaceBlock {
    /** Тир жилы: 1..4 — тонкая … поглотившая. */
    public static final IntegerProperty TIER = IntegerProperty.create("tier", 1, 4);
    /** Рисунок жилы: 0..2, выбирается при установке. */
    public static final IntegerProperty VARIANT = IntegerProperty.create("variant", 0, 2);

    public static final int MIN_TIER = 1;
    public static final int MAX_TIER = 4;

    private static final VoxelShape[] SHAPES_BY_FACES = createShapes();
    private final MultifaceSpreader spreader = new MultifaceSpreader(this);

    private static VoxelShape[] createShapes() {
        VoxelShape[] perFace = new VoxelShape[Direction.values().length];
        for (Direction direction : Direction.values()) {
            perFace[direction.ordinal()] = faceShape(direction);
        }

        VoxelShape[] result = new VoxelShape[1 << Direction.values().length];
        for (int mask = 0; mask < result.length; mask++) {
            VoxelShape combined = Shapes.empty();
            for (Direction direction : Direction.values()) {
                if ((mask & (1 << direction.ordinal())) != 0) {
                    combined = Shapes.or(combined, perFace[direction.ordinal()]);
                }
            }
            result[mask] = combined;
        }
        return result;
    }

    private static VoxelShape faceShape(Direction face) {
        return switch (face) {
            case DOWN -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 1.0D, 16.0D);
            case UP -> Block.box(0.0D, 15.0D, 0.0D, 16.0D, 16.0D, 16.0D);
            case NORTH -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 16.0D, 1.0D);
            case SOUTH -> Block.box(0.0D, 0.0D, 15.0D, 16.0D, 16.0D, 16.0D);
            case WEST -> Block.box(0.0D, 0.0D, 0.0D, 1.0D, 16.0D, 16.0D);
            case EAST -> Block.box(15.0D, 0.0D, 0.0D, 16.0D, 16.0D, 16.0D);
        };
    }

    private static boolean hasSupport(BlockGetter level, BlockPos pos, Direction face) {
        BlockPos supportPos = pos.relative(face);
        BlockState support = level.getBlockState(supportPos);
        return !support.isAir() && (support.isFaceSturdy(level, supportPos, face.getOpposite())
                || support.isSolidRender(level, supportPos));
    }

    private static VoxelShape outline(BlockState state, BlockGetter level, BlockPos pos) {
        int mask = 0;
        for (Direction direction : Direction.values()) {
            if (MultifaceBlock.hasFace(state, direction) && hasSupport(level, pos, direction)) {
                mask |= 1 << direction.ordinal();
            }
        }
        return SHAPES_BY_FACES[mask];
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return Shapes.empty();
    }

    @Override
    public VoxelShape getVisualShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(state, face) && hasSupport(level, pos, face)) return true;
        }
        return false;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(TIER, VARIANT);
    }

    public FleshVeinsBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(defaultBlockState()
                .setValue(TIER, MIN_TIER)
                .setValue(VARIANT, 0));
    }

    /**
     * Новая жила всегда начинается с тонкой t1 и случайного рисунка.
     *
     * <p>Вариация выбирается здесь, а не в {@code getStateForPlacement}, потому
     * что установка идёт и из мира ({@code VeinMutationEngine}), и рукой
     * игрока — оба пути проходят через это место.
     */
    @Override
    public BlockState getStateForPlacement(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        BlockState placed = super.getStateForPlacement(state, level, pos, direction);
        if (placed == null) return null;
        RandomSource random = level instanceof ServerLevel server ? server.getRandom() : RandomSource.create();
        if (!placed.hasProperty(TIER)) return placed;
        // Если жила уже здесь — это рост соседней грани, тир и рисунок не трогаем.
        if (state.is(this)) return placed;
        return placed.setValue(TIER, MIN_TIER).setValue(VARIANT, random.nextInt(3));
    }

    @Override
    @Nullable
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState placed = super.getStateForPlacement(context);
        if (placed == null || !placed.hasProperty(TIER)) return placed;
        return placed.setValue(TIER, MIN_TIER)
                .setValue(VARIANT, context.getLevel().getRandom().nextInt(3));
    }

    @Override
    public void onPlace(BlockState state, net.minecraft.world.level.Level level,
                        BlockPos pos, BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
        }
    }

    @Override
    public void onRemove(BlockState state, net.minecraft.world.level.Level level,
                         BlockPos pos, BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
            // Отсечение дочерней жилы сбрасывает тир у родителя и дальше к
            // источнику. Поглощение (жила → плоть) — не отсечение, а рост
            // цепи: там тир не сбрасывается.
            if (!next.is(ModBlocks.LIVING_FLESH.get())
                    && !next.is(ModBlocks.OSSIFIED_FLESH.get())
                    && !next.is(ModBlocks.FIREPROOF_FLESH.get())
                    && !next.is(ModBlocks.CHARRED_FLESH.get())) {
                com.carnis.mod.world.infection.VeinTierEngine.onChildCut(server, pos);
            }
        }
        super.onRemove(state, level, pos, next, moving);
    }

    @Override
    public MultifaceSpreader getSpreader() {
        return spreader;
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        BlockState updated = super.updateShape(state, direction, neighbor, level, pos, neighborPos);
        if (!updated.is(this)) return updated;

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face) && !hasSupport(level, pos, face)) {
                updated = updated.setValue(MultifaceBlock.getFaceProperty(face), false);
            }
        }

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face)) return updated;
        }
        return Blocks.AIR.defaultBlockState();
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
        VeinMutationEngine.tickVein(level, pos, state, random);
    }

    /** Жила этого блока? Нужно движку мутаций и проверкам сети. */
    public static boolean isVein(BlockState state) {
        return state.is(ModBlocks.FLESH_VEINS.get());
    }

    public static int tierOf(BlockState state) {
        return state.hasProperty(TIER) ? state.getValue(TIER) : MIN_TIER;
    }

    /** Поднять тир на один, не выше {@link #MAX_TIER}. */
    public static BlockState promote(BlockState state) {
        int tier = tierOf(state);
        return tier >= MAX_TIER ? state : state.setValue(TIER, tier + 1);
    }

    /** Опустить тир на один; на минимуме возвращает {@code null} — жилу пора убрать. */
    @Nullable
    public static BlockState demote(BlockState state) {
        int tier = tierOf(state);
        return tier <= MIN_TIER ? null : state.setValue(TIER, tier - 1);
    }
}
