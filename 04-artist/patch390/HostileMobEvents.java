package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.ai.HuntTendrilGoal;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Вешает на враждебных ванильных мобов цель «атаковать щупальца» (дефект N3).
 *
 * <p>Почему событие, а не правка каждого моба. Заражённые мобы мода — наши
 * классы, их цели перечислены в {@code registerGoals}. А зомби, скелет,
 * крипер и паук — ванильные классы: изменить их {@code registerGoals} мод не
 * может, а подменять реестр сущностей ради двух строк — крайняя мера с чужими
 * побочными эффектами. {@code EntityJoinLevelEvent} даёт ровно точку, где моб
 * уже создан, но ещё не начал тикать.
 *
 * <p>Почему проверка {@code level.isClientSide} обязательна. Событие приходит
 * на обеих сторонах. Цели — серверная механика; добавление цели на клиенте
 * привело бы к рассинхрону (клиент считает путь, которого нет на сервере) и к
 * лишней работе каждый раз, когда чанк приходит в поле зрения.
 *
 * <p>Почему {@code priorityGoalSelector(2)}. Это ровно тот же приоритет, на
 * котором у заражённых стоит охота на добычу
 * ({@code InfectedZombieEntity}: {@code goalSelector.addGoal(2, new
 * CarnisHuntPreyGoal(this))}). Так ванильный зомби, у которого есть игрок в
 * прицеле, не бросает его ради щупальца на том же приоритете (приоритеты
 * решаются порядком добавления, а не вытеснением), но и не игнорирует
 * щупальце, если заняться нечем. Ставить выше (например 0) значило бы
 * «щупальце важнее игрока» — это перевернуло бы баланс.
 */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HostileMobEvents {
    private HostileMobEvents() {
    }

    @SubscribeEvent
    public static void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide()) return;
        if (!(event.getEntity() instanceof Mob mob)) return;
        if (!HuntTendrilGoal.eligible(mob)) return;
        // Только ванильные: у мобов других модов своя логика агрессии, и
        // навязывать им нашу цель — значит менять чужой баланс.
        if (!HuntTendrilGoal.vanillaHunter(mob)) return;

        // Идемпотентность: событие приходит и при загрузке чанка из NBT, и при
        // повторном входе моба в мир (телепорт между измерениями). Без проверки
        // цель добавилась бы дважды, и моб дважды за тик искал бы щупальца.
        var selector = mob.goalSelector;
        if (selector.getAvailableGoals().stream()
                .anyMatch(goal -> goal.getGoal() instanceof HuntTendrilGoal)) {
            return;
        }
        selector.addGoal(2, new HuntTendrilGoal(mob));
    }
}
