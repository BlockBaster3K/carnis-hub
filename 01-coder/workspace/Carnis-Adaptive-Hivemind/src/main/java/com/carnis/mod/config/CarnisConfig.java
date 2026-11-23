package com.carnis.mod.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class CarnisConfig {
    public static final Server SERVER;
    public static final ForgeConfigSpec SERVER_SPEC;

    public static final Client CLIENT;
    public static final ForgeConfigSpec CLIENT_SPEC;

    static {
        ForgeConfigSpec.Builder serverBuilder = new ForgeConfigSpec.Builder();
        SERVER = new Server(serverBuilder);
        SERVER_SPEC = serverBuilder.build();

        ForgeConfigSpec.Builder clientBuilder = new ForgeConfigSpec.Builder();
        CLIENT = new Client(clientBuilder);
        CLIENT_SPEC = clientBuilder.build();
    }

    private CarnisConfig() {
    }

    public static final class Server {
        public final ForgeConfigSpec.IntValue infectionBlocksPerTick;
        public final ForgeConfigSpec.IntValue pulsingHeartQueueBonus;
        public final ForgeConfigSpec.IntValue digestorMaxItemsPerCycle;
        public final ForgeConfigSpec.BooleanValue debugLogging;
        public final ForgeConfigSpec.IntValue growthSuppressionRadius;
        public final ForgeConfigSpec.IntValue growthSuppressionStrength;
        public final ForgeConfigSpec.IntValue hiveEyeAuraRadius;
        public final ForgeConfigSpec.BooleanValue hiveEyeBuffsEnabled;
        public final ForgeConfigSpec.BooleanValue hiveEyeDebuffsEnabled;
        public final ForgeConfigSpec.IntValue nervePillarAuraRadius;
        public final ForgeConfigSpec.BooleanValue nervePillarBuffsEnabled;
        public final ForgeConfigSpec.BooleanValue nervePillarDebuffsEnabled;

        private Server(ForgeConfigSpec.Builder builder) {
            builder.comment("Server-side gameplay and performance settings.")
                    .push("server");

            builder.comment("Optimized infection queue settings.")
                    .push("infection_queue");

            infectionBlocksPerTick = builder
                    .comment("Maximum number of queued infection positions processed per server tick.")
                    .defineInRange("blocks_per_tick", 64, 1, 4096);

            pulsingHeartQueueBonus = builder
                    .comment("Additional queued positions a nearby Pulsing Heart may process per server tick.")
                    .defineInRange("pulsing_heart_bonus", 32, 0, 1024);

            builder.pop();

            builder.comment("Living organ settings.")
                    .push("organs");

            digestorMaxItemsPerCycle = builder
                    .comment("Maximum number of item entities a Digestor Pit may consume during one cycle.")
                    .defineInRange("digestor_max_items_per_cycle", 16, 1, 256);

            builder.pop();

            debugLogging = builder
                    .comment("Writes additional Carnis diagnostics to the server log.")
                    .define("debug_logging", false);

            growthSuppressionRadius = builder
                    .comment("Радиус кубической зоны подавления роста флоры вокруг блоков Улья.")
                    .defineInRange("growth_suppression_radius", 8, 1, 32);

            growthSuppressionStrength = builder
                    .comment("Сила подавления роста флоры: от 0 (отключено) до 100 (полное подавление).")
                    .defineInRange("growth_suppression_strength", 80, 0, 100);

            hiveEyeAuraRadius = builder
                    .comment("Радиус действия ауры Ока Улья в блоках.")
                    .defineInRange("hive_eye_aura_radius", 16, 4, 48);

            hiveEyeBuffsEnabled = builder
                    .comment("Включает баффы существ Улья в ауре Ока.")
                    .define("hive_eye_buffs_enabled", true);

            hiveEyeDebuffsEnabled = builder
                    .comment("Включает дебаффы игроков-угроз в ауре Ока.")
                    .define("hive_eye_debuffs_enabled", true);

            nervePillarAuraRadius = builder
                    .comment("Радиус действия ауры Нервного Столба в блоках.")
                    .defineInRange("nerve_pillar_aura_radius", 8, 2, 32);

            nervePillarBuffsEnabled = builder
                    .comment("Включает регенерацию союзников Улья в ауре Нервного Столба.")
                    .define("nerve_pillar_buffs_enabled", true);

            nervePillarDebuffsEnabled = builder
                    .comment("Включает эффект утомления игроков в ауре Нервного Столба.")
                    .define("nerve_pillar_debuffs_enabled", true);

            builder.pop();
        }
    }

    public static final class Client {
        public final ForgeConfigSpec.BooleanValue veinOverlayEnabled;
        public final ForgeConfigSpec.DoubleValue veinOverlayIntensity;
        public final ForgeConfigSpec.BooleanValue phantomEyesEnabled;
        public final ForgeConfigSpec.DoubleValue phantomEyesIntensity;
        public final ForgeConfigSpec.BooleanValue hallucinationSoundsEnabled;
        public final ForgeConfigSpec.DoubleValue hallucinationSoundVolume;
        public final ForgeConfigSpec.BooleanValue atmosphericFogEnabled;
        public final ForgeConfigSpec.DoubleValue neuroSonarOpacity;

        private Client(ForgeConfigSpec.Builder builder) {
            builder.comment("Client-only presentation settings. No gameplay logic is stored here.")
                    .push("client");

            builder.comment("Procedural hallucination overlay settings.")
                    .push("hallucinations");

            veinOverlayEnabled = builder
                    .comment("Enables the procedural pulsing-vein screen overlay.")
                    .define("vein_overlay_enabled", true);

            veinOverlayIntensity = builder
                    .comment("Opacity multiplier for the procedural vein overlay.")
                    .defineInRange("vein_overlay_intensity", 1.0D, 0.0D, 1.0D);

            phantomEyesEnabled = builder
                    .comment("Enables phantom eyes at the edge of the screen.")
                    .define("phantom_eyes_enabled", true);

            phantomEyesIntensity = builder
                    .comment("Size and opacity multiplier for phantom eyes.")
                    .defineInRange("phantom_eyes_intensity", 1.0D, 0.5D, 2.0D);

            hallucinationSoundsEnabled = builder
                    .comment("Enables client-side phantom sounds triggered by server packets.")
                    .define("hallucination_sounds_enabled", true);

            hallucinationSoundVolume = builder
                    .comment("Volume multiplier for phantom hallucination sounds.")
                    .defineInRange("hallucination_sound_volume", 0.75D, 0.0D, 1.0D);

            builder.pop();

            neuroSonarOpacity = builder.comment("Neuro-resonance visor and sonar opacity, 0 to 1.")
                    .defineInRange("neuro_sonar_opacity", 0.65D, 0.0D, 1.0D);

            builder.comment("Infection atmosphere settings.")
                    .push("atmosphere");

            atmosphericFogEnabled = builder
                    .comment("Enables infection-driven atmospheric fog color and distance.")
                    .define("atmospheric_fog_enabled", true);

            builder.pop();
            builder.pop();
        }
    }
}
