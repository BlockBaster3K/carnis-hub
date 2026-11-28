package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;

/**
 * Враждебный ванильный моб считает щупальце угрозой и атакует его.
 *
 * <p>Зачем это нужно. Щупальце — моб улья, который превращает ванильных мобов в
 * заражённых ({@code ParasiticTendrilEntity.doHurtTarget} → {@code
 * InfectionHandler.begin}). До этой цели единственной реакцией ванильного
 * зомби на подходящее щупальце было «ничего»: щупальце подходило и заражало, а
 * моб, который игроку самому угрожает, не сопротивлялся.
 *
 * <p>Кто именно реагирует. Только {@link Monster} — то есть ванильные мобы,
 * которые изначально агрессивны к игроку. Это решение заказчика: мирные
 * животные «на то и мирные», сопротивления не оказывают, их щупальца забирают
 * как раньше.
 *
 * <p>Кого не трогаем:
 * <ul>
 *   <li>мобов улья ({@link HivemindLinkedMob}, свои) — по определению;</li>
 *   <li>уже заражённых — превращение уже произошло, цель теряет смысл;</li>
 *   <li>пауков, зомби и прочих, чей тип мод объявил носителем инфекции, — их
 *       нельзя «спасти» атакой, потому что щупальце всё равно попытается их
 *       заразить и в любом случае заражение идёт через {@code doHurtTarget}.</li>
 * </ul>
 * Последнее — не запрет на драку, а вот что: если моб уже заражён, цель
 * снимается сама (проверка ниже), поэтому «моб бьёт щупальце, пока его
 * инкубируют» не превращается в бессмысленную драку с уже проигранным
 * исходом.
 *
 * <p>Почему {@code NearestAttackableTargetGoal}, а не «свой» Goal. Нам нужна
 * только одна вещь: поставить щупальце в {@code setTarget}. После этого
 * движение и удар делает штатный {@code MeleeAttackGoal}, который уже есть у
 * зомби, скелета, крипера и паука. Писать свой путь и свой удар значило бы
 * дублировать ванильную логику и разойтись с ней в деталях (перезарядка атаки,
 * высота цели, отбрасывание).
 */
public final class HuntTendrilGoal extends NearestAttackableTargetGoal<ParasiticTendrilEntity> {
    /**
     * Дистанция поиска. У ванильного зомби {@code FOLLOW_RANGE} = 35 блоков;
     * берём меньше, чтобы моб не бросал игрока ради щупальца на горизонте, но
     * достаточно, чтобы заметить угрозу до заражения: щупальце движется со
     * скоростью 0.27, удар — на дистанции атаки.
     */
    private static final double SEARCH_RADIUS = 16.0D;
    /**
     * Период опроса, в тиках.
     *
     * <p>⚠️ Это НЕ дистанция. В {@code NearestAttackableTargetGoal(int i, …)}
     * аргумент {@code i} уходит в {@code reducedTickDelay(i)} — период опроса,
     * а дальность берётся из {@code getFollowDistance()} моба. Первая версия
     * передавала туда 16 «как радиус» и получила бы опрос раз в 16 тиков при
     * дальности {@code FOLLOW_RANGE}=35: медленно и слишком далеко. Поэтому
     * дистанция ставится явно в {@link #targetConditions}, а период — здесь.
     */
    private static final int SCAN_INTERVAL = 10;

    public HuntTendrilGoal(Mob hunter) {
        super(hunter, ParasiticTendrilEntity.class, SCAN_INTERVAL, false, false,
                HuntTendrilGoal::isThreat);
        // Родитель построил условия по FOLLOW_RANGE моба; заменяем их на
        // свою дистанцию. Поле `targetConditions` — protected, поэтому
        // присваивание здесь законно.
        this.targetConditions = net.minecraft.world.entity.ai.targeting.TargetingConditions
                .forCombat()
                .range(SEARCH_RADIUS)
                .selector(HuntTendrilGoal::isThreat);
    }

    /**
     * Может ли этот моб вообще охотиться на щупальца.
     *
     * <p>Список типов ванильных монстров намеренно оставлен {@link Monster}:
     * {@code Monster} — это ровно «изначально враждебные к игроку» (зомби,
     * скелет, крипер, паук, эндермен, иллиджеры…). Мод не перечисляет их
     * поимённо, поэтому новая ванильная нежить тоже получит цель, а мирная
     * корова — нет.
     */
    public static boolean eligible(Mob mob) {
        return mob instanceof Monster && !(mob instanceof HivemindLinkedMob)
                && !(mob instanceof ParasiticTendrilEntity);
    }

    private static boolean isThreat(LivingEntity candidate) {
        if (!(candidate instanceof ParasiticTendrilEntity tendril)) return false;
        if (!tendril.isAlive()) return false;
        // Щупальце живёт один удар: после doHurtTarget оно discard()'ится.
        // Ловить «мёртвое, но ещё в мире» незачем.
        return true;
    }

    /**
     * Охотник — ванильный моб, а не чужой.
     *
     * <p>Проверяется namespace типа. Без этого {@link Monster} пропускает и
     * мобов других модов, формально враждебных игроку: навязывать им нашу
     * цель — значит менять чужой баланс, а мод обязан вести себя только со
     * своим окружением.
     */
    public static boolean vanillaHunter(Mob mob) {
        ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType());
        return id != null && "minecraft".equals(id.getNamespace());
    }
}
