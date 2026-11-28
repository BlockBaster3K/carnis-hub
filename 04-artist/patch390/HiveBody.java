package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.EntityCollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Тело улья: плоть и мембрана, сквозь которые мобы Carnis проходят.
 *
 * <p><b>Задача.</b> Улей растёт под землёй; порождённые им мобы стоят внутри
 * твёрдой плоти — поиск пути считает её стеной, выхода нет. Снаружи та же
 * стена не пускает внутрь. Заказчик: «пусть мобы Carnis имеют возможность
 * проходить сквозь блоки улья при желании», не телепортом.
 *
 * <p><b>Что проверено по исходникам 1.20.1</b> (это и определило конструкцию):
 * <ul>
 *   <li>физика — {@code BlockCollisions} — спрашивает коллизию
 *       <b>с сущностью</b>: {@code CollisionContext.of(entity)}; отсюда можно
 *       достать {@code EntityCollisionContext.getEntity()};</li>
 *   <li>поиск пути — {@code WalkNodeEvaluator.getBlockPathTypeRaw} →
 *       {@code isPathfindable} → {@code BlockBehaviour} — проверяет
 *       {@code blockstate.isCollisionShapeFullBlock(level, pos)}, а тот берёт
 *       {@code cache.collisionShape} — коллизию, посчитанную <b>без
 *       сущности</b>. Значит «проходимость по типу моба» в коллизии путь не
 *       открывает: моб провалился бы в плоть и всё равно стоял без маршрута;</li>
 *   <li>{@code PathNavigation.createPath}: если путь уже есть и цель та же,
 *       старый путь возвращается <b>без пересчёта</b>. Поэтому после входа в
 *       режим прохода путь надо сбрасывать — иначе моб год будет идти
 *       маршрутом, построенным вокруг стены.</li>
 * </ul>
 *
 * <p><b>Отсюда решение.</b> Коллизия пуста, если сущность в контексте — моб
 * пространства имён {@code carnis}. Тогда физика его пропускает. Маршрут при
 * этом остаётся доступным, потому что такой моб сам, по своей воле, строит
 * его через плоть: {@link #isPathfindable} для него всегда {@code true}, а
 * {@code HivePhasing} сбрасывает кэш пути при входе в режим прохода и
 * компенсирует гравитацию, пока моб внутри плоти (иначе он падал бы сквозь
 * пол улья).
 *
 * <p><b>Игрока это не касается.</b> У игрока нет namespace {@code carnis},
 * поэтому он видит обычную твёрдую плоть. Ванильные мобы и животные — тоже.
 *
 * <p><b>Почему не отдельный блок-двойник.</b> Плоть должна остаться плотью:
 * тикать, расти, заражать, участвовать в {@code HiveNetwork}. Меняется только
 * коллизия, и только для своих.
 */
public final class HiveBody {
    /** Пространство имён, которому разрешён проход. */
    public static final String HIVE_NAMESPACE = "carnis";

    private HiveBody() {
    }

    /** Блок считается телом улья? */
    public static boolean isHiveBody(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get())
                || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(ModBlocks.FIREPROOF_FLESH.get())
                || state.is(ModBlocks.CHARRED_FLESH.get())
                || state.is(ModBlocks.HIVE_MEMBRANE.get());
    }

    /**
     * Моб этого мода — тот, кому разрешён проход.
     *
     * <p>Проверяется и {@code Mob} (чтобы не пропустить снаряды), и namespace
     * типа сущности (чтобы не пропустить чужих мобов).
     */
    public static boolean mayPhase(Entity entity) {
        if (!(entity instanceof Mob mob)) return false;
        var id = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType());
        return id != null && HIVE_NAMESPACE.equals(id.getNamespace());
    }

    /** Сущность из контекста коллизии, если он её несёт. */
    private static Entity contextEntity(CollisionContext context) {
        if (context instanceof EntityCollisionContext entityContext) {
            return entityContext.getEntity();
        }
        return null;
    }

    /**
     * Коллизия для физики: своим мобам — пусто, всем остальным — обычная.
     *
     * <p>Вызывать из {@code getCollisionShape} блока.
     */
    public static VoxelShape collisionFor(BlockState state, BlockGetter level, BlockPos pos,
                                          CollisionContext context, VoxelShape solid) {
        Entity entity = contextEntity(context);
        if (entity != null && mayPhase(entity)) return Shapes.empty();
        return solid;
    }

    /**
     * Проходимость для поиска пути.
     *
     * <p>Здесь нельзя опереться на контекст: его нет. Поэтому плоть объявлена
     * проходимой для всех, кто строит маршрут, — но маршрут строится только
     * по решению самого моба ({@code HivePhasing} запускает поиск лишь для
     * своих). Игрок путь не строит вовсе, а ванильный моб к плоти не пойдёт:
     * его цель — игрок, а не улей.
     *
     * <p>Плата за это — плоть перестаёт быть «полным блоком» для навигации
     * всех: ванильный моб, преследующий игрока за стеной плоти, попробует
     * пройти сквозь неё и упрётся. Это допустимо: альтернатива — мобы улья,
     * замурованные в собственном улье навсегда.
     */
    public static boolean pathfindable(BlockState state, BlockGetter level, BlockPos pos,
                                       net.minecraft.world.level.pathfinder.PathComputationType type) {
        return type == net.minecraft.world.level.pathfinder.PathComputationType.LAND;
    }

    /** Открыть ли мобу проход в этой клетке — для проверок урона и отладки. */
    public static boolean passableFor(ServerLevel level, BlockPos pos, Entity entity) {
        BlockState state = level.getBlockState(pos);
        return isHiveBody(state) && entity instanceof Mob && mayPhase(entity);
    }

    /** Направление от сущности к клетке плоти, если она вплотную. */
    public static Direction hiveSide(BlockGetter level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            BlockPos next = pos.relative(direction);
            if (isHiveBody(level.getBlockState(next))) return direction;
        }
        return null;
    }
}
