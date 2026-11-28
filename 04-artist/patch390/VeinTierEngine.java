package com.carnis.mod.world.infection;

import com.carnis.mod.block.FleshVeinsBlock;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

/**
 * Каскад тиров плотоных жил: рост утолщает, отсечение истончает.
 *
 * <p><b>Модель.</b> Жила — это «сосуд», по которому плоть гонит массу от
 * источника (блока плоти) к растущему кончику. Чем длиннее выросшая цепь, тем
 * больше давления держат ближние к источнику участки — они и толще. Отсюда
 * правила концепта:
 * <ul>
 *   <li>дочерняя жила выросла дальше от источника → родитель {@code +1} тир,
 *       и импульс идёт дальше к источнику (каскад, не выше t4);</li>
 *   <li>дочернюю отсекли → родитель {@code -1} тир, импульс идёт к источнику;
 *       на нуле жила исчезает;</li>
 *   <li>жила t4 получает ещё один импульс («t5») → она поглощает свою клетку
 *       и становится полноценным {@code flesh_block}.</li>
 * </ul>
 *
 * <p><b>Почему каскад, а не только «родитель +1».</b> Если утолщать лишь
 * непосредственного родителя, у длинной цепи окажется толстым один участок
 * посреди тонкой — визуально это разрыв, а не «жила, наливающаяся от
 * источника». Ровный спад t4→t3→t2→t1 вдоль цепи и есть картинка концепта.
 *
 * <p><b>Почему импульс ходит по цепи, а не по расстоянию.</b> Цепь может
 * ветвиться и изгибаться; расстояние «по воздуху» сквозь несколько блоков
 * плоти дало бы утолщение там, где жилы нет. Идём по соседним клеткам жил —
 * это ровно то, что видит игрок.
 *
 * <p><b>Почему это дешёво.</b> Импульс запускается только на событие роста
 * (раз в несколько секунд на жилу) и на разрушение. Глубина хода ограничена
 * {@link #MAX_CASCADE}, поэтому даже кольцо жил не зациклит обход.
 */
public final class VeinTierEngine {
    /**
     * Предел шагов импульса.
     *
     * <p>Шаг идёт в кубе радиуса 2 (см. {@link #stepTowardSource}), то есть
     * сокращает расстояние не меньше чем на 1. При радиусе поиска выхода из
     * источника 4 ({@link #SOURCE_RADIUS}) и разумной длине цепи 24 шага
     * покрывают любую жилу вокруг одного блока плоти. Число ограничивает не
     * длину «по задумке», а защиту от кольца жил: убывание расстояния и так
     * гарантирует завершение, но явный предел читается легче.
     */
    private static final int MAX_CASCADE = 24;
    /** Радиус поиска источника — тот же, что у движка мутаций. */
    private static final int SOURCE_RADIUS = 4;
    private static final Direction[] DIRECTIONS = Direction.values();

    private VeinTierEngine() {
    }

    /**
     * Жила в {@code parentPos} вырастила дочернюю в {@code childPos}.
     *
     * <p>Вызывается из {@code VeinMutationEngine.spread} сразу после успешной
     * установки: только там известно, что рост действительно произошёл.
     */
    public static void onChildGrown(ServerLevel level, BlockPos parentPos) {
        if (!FleshVeinsBlock.isVein(level.getBlockState(parentPos))) return;
        BlockPos source = nearestSource(level, parentPos);
        if (source == null) return;      // цепи без источника не растут
        push(level, parentPos, source, 0);
    }

    /**
     * Жила в {@code pos} отсечена: её родитель должен сбросить тир.
     *
     * <p>Вызывается из {@code FleshVeinsBlock.onRemove}. Если клетку заняла
     * плоть (поглощение), откат не нужен — цепь не оборвалась, а усилилась;
     * это проверяет сам блок перед вызовом.
     */
    public static void onChildCut(ServerLevel level, BlockPos pos) {
        BlockPos source = nearestSource(level, pos);
        if (source == null) return;
        // ⚠️ `pos` к этому моменту уже НЕ жила: onRemove вызывается после
        // того, как блок сменился. Импульс обязан начинаться с родителя —
        // соседней жилы, ближайшей к источнику. Первая версия начинала с
        // `pos`, упиралась в `!isVein` и молча выходила, то есть откат не
        // работал вовсе.
        BlockPos parent = null;
        double best = pos.distSqr(source);
        for (Direction direction : DIRECTIONS) {
            BlockPos next = pos.relative(direction);
            if (!level.hasChunkAt(next)) continue;
            if (!FleshVeinsBlock.isVein(level.getBlockState(next))) continue;
            double dist = next.distSqr(source);
            if (dist < best) {
                best = dist;
                parent = next;
            }
        }
        if (parent == null) return;
        pull(level, parent, source, 0);
    }

    /** Импульс роста: утолщаем по цепи к источнику, на t4 — поглощение. */
    private static void push(ServerLevel level, BlockPos from, BlockPos source, int depth) {
        if (depth > MAX_CASCADE) return;
        BlockPos cursor = from;
        for (int step = 0; step < MAX_CASCADE; step++) {
            BlockState state = level.getBlockState(cursor);
            if (!FleshVeinsBlock.isVein(state)) return;

            int tier = FleshVeinsBlock.tierOf(state);
            if (tier >= FleshVeinsBlock.MAX_TIER) {
                // «t5»: жила переполнена и поглощает свою клетку.
                absorb(level, cursor, state);
                return;
            }

            level.setBlock(cursor, state.setValue(FleshVeinsBlock.TIER, tier + 1),
                    net.minecraft.world.level.block.Block.UPDATE_ALL);

            BlockPos next = stepTowardSource(level, cursor, source);
            if (next == null) return;
            cursor = next;
        }
    }

    /** Импульс отсечения: истончаем по цепи; на нуле жила исчезает. */
    private static void pull(ServerLevel level, BlockPos from, BlockPos source, int depth) {
        if (depth > MAX_CASCADE) return;
        BlockPos cursor = from;
        for (int step = 0; step < MAX_CASCADE; step++) {
            BlockState state = level.getBlockState(cursor);
            if (!FleshVeinsBlock.isVein(state)) return;

            BlockState demoted = FleshVeinsBlock.demote(state);
            if (demoted == null) {
                // Тоньше t1 некуда: жилы больше нет, но цепь продолжает
                // откатываться — иначе ближние к источнику остались бы
                // утолщёнными без причины.
                BlockPos next = stepTowardSource(level, cursor, source);
                level.removeBlock(cursor, false);
                if (next == null) return;
                cursor = next;
                continue;
            }
            level.setBlock(cursor, demoted, net.minecraft.world.level.block.Block.UPDATE_ALL);
            BlockPos next = stepTowardSource(level, cursor, source);
            if (next == null) return;
            cursor = next;
        }
    }

    /** Жила t4, получившая ещё импульс, становится блоком плоти. */
    private static void absorb(ServerLevel level, BlockPos pos, BlockState state) {
        // Тот же выбор, что у движка мутаций: после долгой огневой адаптации
        // плоть окремневает. Иначе поглощение давало бы живую плоть там, где
        // всё вокруг уже окремнело.
        BlockState replacement = com.carnis.mod.world.CarnisWorldData.get(level)
                .getFireAdaptation() >= 300L
                ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                : ModBlocks.LIVING_FLESH.get().defaultBlockState();
        level.setBlock(pos, replacement,
                net.minecraft.world.level.block.Block.UPDATE_ALL);
        level.levelEvent(2001, pos, net.minecraft.world.level.block.Block.getId(state));
        level.playSound(null, pos, com.carnis.mod.init.ModSounds.HIVE_SPREAD.get(),
                net.minecraft.sounds.SoundSource.BLOCKS, 0.8F, 0.7F);
    }

    /**
     * Ближайшая к источнику клетка жилы рядом — направление импульса.
     *
     * <p><b>Почему радиус 2, а не строгая соседняя клетка.</b> Жилы стоят на
     * гранях блоков-хозяев, и движок роста ставит новую жилу в
     * {@code hostPos.relative(face)} — это клетка <b>по диагонали</b> или через
     * одну от родителя, но почти никогда не вплотную. Первая версия искала
     * только шесть соседей, поэтому после первого шага цепь «обрывалась» и
     * каскад на деле не шёл: утолщался один родитель.
     *
     * <p>Ищем в кубе Чебышёва радиуса 2 и требуем строгого приближения к
     * источнику — это гарантирует, что шаг завершится: расстояние монотонно
     * убывает, значит циклов нет.
     */
    private static BlockPos stepTowardSource(ServerLevel level, BlockPos pos, BlockPos source) {
        BlockPos best = null;
        double bestDist = pos.distSqr(source);
        for (int dx = -2; dx <= 2; dx++) {
            for (int dy = -2; dy <= 2; dy++) {
                for (int dz = -2; dz <= 2; dz++) {
                    if (dx == 0 && dy == 0 && dz == 0) continue;
                    BlockPos next = pos.offset(dx, dy, dz);
                    if (!level.hasChunkAt(next) || level.isOutsideBuildHeight(next)) continue;
                    if (!FleshVeinsBlock.isVein(level.getBlockState(next))) continue;
                    double dist = next.distSqr(source);
                    if (dist < bestDist) {
                        bestDist = dist;
                        best = next;
                    }
                }
            }
        }
        return best;
    }

    /**
     * Ближайший блок плоти в радиусе {@link #SOURCE_RADIUS} по манхэттену.
     *
     * <p>Ищем именно блок плоти, а не «что-то похожее»: источник — это
     * {@code LIVING_FLESH} и его окремневшие/обгорелые варианты. Окремневшая
     * плоть тоже источник: жилы рядом с ней растут и тируются так же.
     */
    private static BlockPos nearestSource(ServerLevel level, BlockPos center) {
        Map<BlockPos, Integer> visited = new HashMap<>();
        Deque<BlockPos> queue = new ArrayDeque<>();
        queue.add(center);
        visited.put(center, 0);
        while (!queue.isEmpty()) {
            BlockPos current = queue.poll();
            int dist = visited.get(current);
            if (dist > SOURCE_RADIUS) continue;
            for (Direction direction : DIRECTIONS) {
                BlockPos next = current.relative(direction);
                if (visited.containsKey(next)) continue;
                if (!level.hasChunkAt(next) || level.isOutsideBuildHeight(next)) continue;
                BlockState state = level.getBlockState(next);
                if (isFlesh(state)) return next;
                if (FleshVeinsBlock.isVein(state) && dist + 1 < SOURCE_RADIUS) {
                    visited.put(next, dist + 1);
                    queue.add(next);
                }
            }
        }
        return null;
    }

    private static boolean isFlesh(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get())
                || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(ModBlocks.FIREPROOF_FLESH.get())
                || state.is(ModBlocks.CHARRED_FLESH.get());
    }

    /** Есть ли у клетки жила хотя бы с одной стороны — для диагностики и тестов. */
    public static boolean hasAnyFace(BlockState state) {
        if (!FleshVeinsBlock.isVein(state)) return false;
        for (Direction direction : DIRECTIONS) {
            if (MultifaceBlock.hasFace(state, direction)) return true;
        }
        return false;
    }
}
