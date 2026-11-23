package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.LanguageProvider;

public final class ModLanguageProvider extends LanguageProvider {
    private static final String EN_US = "en_us";
    private static final String RU_RU = "ru_ru";

    private final String locale;

    public ModLanguageProvider(PackOutput output, String locale) {
        super(output, CarnisMod.MOD_ID, locale);
        this.locale = locale;
    }

    @Override
    protected void addTranslations() {
        switch (locale) {
            case EN_US -> addEnglishTranslations();
            case RU_RU -> addRussianTranslations();
            default -> throw new IllegalStateException(
                    "Unsupported Carnis language provider locale: " + locale
            );
        }
    }

    private void addEnglishTranslations() {
        add("carnis.tab", "Carnis: Adaptive Hivemind");
        add("item.carnis.parasitic_tendril_spawn_egg", "Parasitic Tendril Spawn Egg");
        add("tooltip.carnis.parasitic_tendril_spawn_egg", "Spawns a parasitic tendril.");
        add("item.carnis.hive_sentinel_spawn_egg", "Hive Sentinel Spawn Egg");
        add("tooltip.carnis.hive_sentinel_spawn_egg", "Spawns a hive sentinel.");
        add("item.carnis.cerebral_nexus_spawn_egg", "Cerebral Nexus Spawn Egg");
        add("tooltip.carnis.cerebral_nexus_spawn_egg", "Spawns a cerebral nexus.");
        add("tooltip.carnis.biomass_remains", "Organic remains left by a host.");
        add("tooltip.carnis.flesh_bulb", "An incubating organic sac.");
        add("tooltip.carnis.sinew_spikes", "Piercing growths slow creatures.");
        add("tooltip.carnis.biomass_maggot_spawn_egg", "Spawns a biomass maggot.");
        add("codex.carnis.previous", "< Back");
        add("codex.carnis.next", "Next >");
        add("codex.carnis.tab.0", "Organogenesis");
        add("codex.carnis.tab.1", "Biocenosis");
        add("codex.carnis.tab.2", "Aberrations");
        add("codex.carnis.tab.3", "Biotechnology");
        add("codex.carnis.entry.0.title", "Pulsing Heart");
        add("codex.carnis.entry.0.body", "The colony core pulses every 100 ticks. Known flesh and veins measure growth within 32 blocks; the pulse itself reaches 8.");
        add("codex.carnis.entry.0.note", "The heart counts only tissue it has discovered.");
        add("codex.carnis.entry.1.title", "Order of organs");
        add("codex.carnis.entry.1.body", "At 25, 50, 75 and 100 infected blocks the Hive develops an eye, sentinel, pool and pillar. Growth requires living flesh 8–24 blocks away.");
        add("codex.carnis.entry.1.note", "Organs grow where the cell finds a suitable place.");
        add("codex.carnis.entry.2.title", "Hive Eye");
        add("codex.carnis.entry.2.body", "The sensor detects outsiders within 18 blocks and alerts free Hive mobs within 28 blocks.");
        add("codex.carnis.entry.2.note", "The scream is heard before the pupil is seen.");
        add("codex.carnis.entry.3.title", "Stomach Pool");
        add("codex.carnis.entry.3.body", "Acid dissolves items and living tissue. Livestock killed within it yields 20 biomass to a nearby heart, or 30 for a cow.");
        add("codex.carnis.entry.3.note", "Five damage per second is reason enough to stay out.");
        add("codex.carnis.entry.4.title", "Nerve Pillar");
        add("codex.carnis.entry.4.body", "The pillar blocks new thermal shock within 32 blocks. Its shield reduces ignition of Hive forms but does not make flesh fireproof.");
        add("codex.carnis.entry.4.note", "Destroy the anchor first. Then cleanse the site.");
        add("codex.carnis.entry.5.title", "Sentinel and Nexus");
        add("codex.carnis.entry.5.body", "A psychic anchor draws livestock into a trance and guides it to a pool. With four organs and 200 biomass the heart can become a Cerebral Nexus.");
        add("codex.carnis.entry.5.note", "Two daughter hearts appear on known flesh 48–64 blocks away.");
        add("codex.carnis.entry.6.title", "Biomass Remains");
        add("codex.carnis.entry.6.body", "A host dying on solid ground leaves loose remains. They slow outsiders and Hive creatures alike; maggots appear near carrion.");
        add("codex.carnis.entry.6.note", "No sample was obtained in water or without support.");
        add("codex.carnis.entry.7.title", "Biomass Maggot");
        add("codex.carnis.entry.7.body", "The maggot seeks remains within 16 blocks. Two meals awaken its burrowing instinct; one minute on flesh is enough.");
        add("codex.carnis.entry.7.note", "It chooses loose soil or flesh, not stone.");
        add("codex.carnis.entry.8.title", "Maturing Cocoon");
        add("codex.carnis.entry.8.body", "The Flesh Bulb attaches to ceilings or floors. After 60–90 seconds its heartbeat quickens and the sac bursts, releasing tendrils.");
        add("codex.carnis.entry.8.note", "Time passes only in loaded areas.");
        add("codex.carnis.entry.9.title", "Tendril: implantation");
        add("codex.carnis.entry.9.body", "Contact infects a peaceful host with 85% probability or a monster with 45%; armor reduces the monster chance to 30%. The parasite vanishes after its attempt.");
        add("codex.carnis.entry.9.note", "Failure brings a hiss and a minor wound.");
        add("codex.carnis.entry.10.title", "Four stages");
        add("codex.carnis.entry.10.body", "Up to 10 seconds: incubation; up to 25: veins and growths; up to 30: rupture and soil infection. Then a monster mutates and a peaceful host decomposes.");
        add("codex.carnis.entry.10.note", "In the third stage the wound can kill before transformation.");
        add("codex.carnis.entry.11.title", "Infected Zombie");
        add("codex.carnis.entry.11.body", "Its right arm has grown into a bone blade; tendrils frame its torn head. Near remains it stops and consumes biomass.");
        add("codex.carnis.entry.11.note", "While feeding, its gaze holds one direction.");
        add("codex.carnis.entry.12.title", "Infected Skeleton");
        add("codex.carnis.entry.12.body", "A bone scythe replaces its weapon. A sprouting nerve and ribcage core glow red; a sweep can strike nearby targets.");
        add("codex.carnis.entry.12.note", "An empty eye socket does not mean it cannot see.");
        add("codex.carnis.entry.13.title", "Infected Creeper");
        add("codex.carnis.entry.13.body", "Swollen sacs shudder before rupture. Instead of a normal explosion it releases spores, poisons living creatures and leaves veins on solid faces.");
        add("codex.carnis.entry.13.note", "Frantic antennae signal imminent detonation.");
        add("codex.carnis.entry.14.title", "Flesh Amalgam");
        add("codex.carnis.entry.14.body", "A titanic symbiote forms when infected creatures fuse near a heart. Bone plates and acid change with Hive adaptation.");
        add("codex.carnis.entry.14.note", "A weakened Amalgam consumes remains and lesser forms; beware its shockwave and corrosive bile.");
        add("codex.carnis.entry.15.title", "Pneumatic Inoculator");
        add("codex.carnis.entry.15.body", "A dart carries a viral strain or a purifying compound. Account for projectile drop and cover; firing consumes a suitable carried dart.");
        add("codex.carnis.entry.15.note", "The purifying compound reduces player infection by 35.");
        add("codex.carnis.entry.16.title", "Bio-Purifier");
        add("codex.carnis.entry.16.body", "A stream of fire sterilizes living and ossified flesh, leaving charred tissue. Thermal shock usually affects the infected area.");
        add("codex.carnis.entry.16.note", "An active nerve pillar blocks new thermal shock.");
        add("codex.carnis.entry.17.title", "Neuro armor");
        add("codex.carnis.entry.17.body", "Woven tendons connect the armor to the wearer’s nervous system. Each protected piece reduces infectious exposure by a quarter.");
        add("codex.carnis.entry.17.note", "A full set hides its wearer from the Eye, but does not promise invisibility to all.");
        add("subtitles.carnis.inoculator_fire", "Inoculator fires");
        add("subtitles.carnis.dart_hit", "Dart hits");
        add("tooltip.carnis.flesh_bulb.mechanics", "An incubation sac that can attach to ceilings and floors.");
        add("tooltip.carnis.flesh_bulb.lore", "The muffled, rapid heartbeat of a maturing brood can be heard inside.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Deals piercing damage and slows any creature that steps on it.");
        add("tooltip.carnis.sinew_spikes.lore", "Taut sinews respond to the slightest vibration of footsteps.");
        add("tooltip.carnis.biomass_maggot.mechanics", "A voracious scavenger. Devours organic remains and pupates in soil.");
        add("tooltip.carnis.biomass_maggot.lore", "The first link in the Hive’s parasitic cycle.");
        add("item.carnis.infected_zombie_spawn_egg", "Infected Zombie Spawn Egg");
        add("entity.carnis.infected_zombie", "Infected Zombie");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Spawns an infected zombie.");
        add("item.carnis.antibiotics", "Antibiotics");
        add("effect.carnis.immunosuppression", "Immunosuppression");
        add("tooltip.carnis.antibiotics", "Prevents exposure for 3 minutes.");
        add("entity.carnis.parasitic_tendril", "Parasitic Tendril");
        add("entity.carnis.hive_sentinel", "Hive Sentinel");
        add("entity.carnis.cerebral_nexus", "Cerebral Nexus");
        add("effect.carnis.incubating", "Incubating");
        add("subtitles.carnis.flamethrower_fire", "Flamethrower roars");
        add("subtitles.carnis.amalgam_roar", "Amalgam roars");
        add("codex.carnis.chapter.0", "Inception & Biomes");
        add("codex.carnis.body.0", "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.");
        add("codex.carnis.chapter.1", "Adaptive Hivemind");
        add("codex.carnis.body.1", "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.");
        add("codex.carnis.chapter.2", "Hive Organs & Flora");
        add("codex.carnis.body.2", "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.");
        add("codex.carnis.chapter.3", "Medical & Armor Weaving");
        add("codex.carnis.body.3", "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.");
        add("codex.carnis.chapter.4", "Mutants & Amalgamation");
        add("codex.carnis.body.4", "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.");
        add("entity.carnis.flesh_spat", "Flesh Spat");
        add("item.carnis.flesh_spat", "Flesh Spat");
        add("tooltip.carnis.flesh_spat", "A glob of infectious tissue.");
        add("subtitles.carnis.heartbeat_loop", "Heart beats");
        add("item.carnis.research_journal", "Codex Carnis");
        add("tooltip.carnis.research_journal", "A field guide to the hive.");
        add("item.carnis.tainted_sludge_bucket", "Tainted Sludge Bucket");
        add("item.carnis.bone_scythe_arm", "Bone Scythe Arm");
        add("block.carnis.tainted_sludge", "Tainted Sludge");
        add("fluid_type.carnis.tainted_sludge", "Tainted Sludge");
        add("tooltip.carnis.tainted_sludge_bucket", "A bucket of infectious sludge.");
        add("tooltip.carnis.bone_scythe_arm", "A jagged bone blade.");
        add("subtitles.carnis.amalgam_step", "Flesh Amalgam squelches");
        add("block.carnis.flesh_veins", "Flesh Veins");
        add("tooltip.carnis.flesh_veins", "Organic growth on exposed surfaces.");

        add("entity.carnis.infected_skeleton", "Infected Skeleton");
        add("item.carnis.infected_skeleton_spawn_egg", "Infected Skeleton Spawn Egg");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Spawns an infected skeleton.");
        add("entity.carnis.infected_creeper", "Infected Creeper");
        add("item.carnis.infected_creeper_spawn_egg", "Infected Creeper Spawn Egg");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Spawns an infected creeper.");
        add("entity.carnis.infected_spider", "Infected Spider");
        add("item.carnis.infected_spider_spawn_egg", "Infected Spider Spawn Egg");
        add("tooltip.carnis.infected_spider_spawn_egg", "Spawns an infected spider.");
        add("item.carnis.neuro_resonator_chestplate", "Neuro-Resonator Chestplate");
        add("item.carnis.neuro_resonator_leggings", "Neuro-Resonator Leggings");
        add("item.carnis.neuro_resonator_boots", "Neuro-Resonator Boots");
        add("block.carnis.flesh_bulb", "Flesh Bulb");
        add("block.carnis.biomass_remains", "Biomass Remains");
        add("block.carnis.sinew_spikes", "Sinew Spikes");
        add("entity.carnis.biomass_maggot", "Biomass Maggot");
        add("item.carnis.biomass_maggot_spawn_egg", "Biomass Maggot Spawn Egg");
        add("item.carnis.neural_binding_matrix", "Neural Binding Matrix");
        add("tooltip.carnis.neuro_resonator_chestplate", "A biological chestplate reduces infection exposure.");
        add("tooltip.carnis.neuro_resonator_leggings", "Biological leggings reduce infection exposure.");
        add("tooltip.carnis.neuro_resonator_boots", "Biological boots reduce infection exposure.");
        add("tooltip.carnis.neural_binding_matrix", "Weave into armor at an anvil for five levels.");
        add("block.carnis.nerve_pillar", "Nerve Pillar");
        add("item.carnis.pneumatic_inoculator", "Pneumatic Inoculator");
        add("item.carnis.viral_dart", "Viral Dart");
        add("item.carnis.purification_dart", "Purification Dart");
        add("entity.carnis.viral_dart", "Viral Dart");
        add("entity.carnis.purification_dart", "Purification Dart");
        add("death.attack.carnis_tainted_sludge", "%1$s dissolved in tainted sludge");
        add("death.attack.purification_dart", "%1$s was purified by a dart");
        add("death.attack.purification_dart.player", "%1$s was purified by %2$s");
        add("tooltip.carnis.nerve_pillar", "Placement halves remaining shock time in this chunk.");
        add("tooltip.carnis.pneumatic_inoculator", "Right-click to fire a carried dart; 15-tick cooldown.");
        add("tooltip.carnis.purification_dart.mechanics", "Players: removes 35 infection and clears nausea, blindness and slowness.");
        add("tooltip.carnis.purification_dart.protocol", "Regresses infected humanoids; damages and stuns major Hive organisms.");
        add("tooltip.carnis.viral_dart.mechanics", "Players: adds 25 infection and causes weakness.");
        add("tooltip.carnis.viral_dart.protocol", "Accelerates livestock incubation; mutates zombies, skeletons and creepers.");
        add("tooltip.carnis.dart.use", "Load in the Pneumatic Inoculator and fire at the target.");
        add("subtitles.carnis.hive_alarm", "Hive eye screams");
        add("subtitles.carnis.hive_ambient_drone", "The Hive breathes");
        add("subtitles.carnis.creeper_rupture", "Biological rupture");
        add("entity.carnis.hive_spore_cloud", "Hive Spore Cloud");
        add("tooltip.carnis.purification_serum.mechanics", "Drink to remove 35 infection points.");
        add("tooltip.carnis.purification_serum.use", "Use directly or craft into purification darts.");
        add("entity.carnis.inoculator_dart", "Inoculator Dart");
        add("tooltip.carnis.viral_dart", "Adds 25 infection to players and causes weakness.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.neural_moss.mechanics", "Slows outsiders; spreads near water or Hive tissue.");
        add("tooltip.carnis.neural_moss.lore", "A living carpet listens for unfamiliar footsteps.");
        add("tooltip.carnis.creeping_tendrils", "Climb the tendrils attached to solid flesh.");
        add("tooltip.carnis.pustule_cluster", "Step on it without sneaking to burst infectious spores.");
        add("tooltip.carnis.stomach_pool", "Corrosive tissue dissolves items into biomass.");
        add("tooltip.carnis.ossified_flesh", "Hardened tissue spreads the hive.");
        add("tooltip.carnis.fireproof_flesh", "Adapted tissue resistant to flame.");
        add("tooltip.carnis.veins", "Living veins carry infection through wood.");
        add("tooltip.carnis.pulsing_heart", "The hive heart accelerates nearby infection.");
        add("tooltip.carnis.hive_eye", "Detects intruders and alerts nearby Hive members.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Spawns a Flesh Amalgam.");
        add("tooltip.carnis.purification_serum", "Drink to remove 35 infection points.");
        add("effect.carnis.thermal_shock", "Thermal Shock");
        add("subtitles.carnis.purifier_ignite", "Purifier ignites");
        add("subtitles.carnis.purifier_loop", "Purifier fires");
        add("tooltip.carnis.bio_purifier", "Hold use: 6.5-block cone of flame.");
        add("tooltip.carnis.neuro_resonator_helmet", "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.");
        add("itemGroup.carnis", "Carnis: Adaptive Hivemind");

        add("death.attack.necrotic_consumption", "%1$s was consumed by the hivemind");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Creeping Tendrils");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Pustule Cluster");
        add(ModBlocks.STOMACH_POOL.get(), "Stomach Pool");
        add(ModBlocks.SPORE_SPROUT.get(), "Spore Sprout");
        add(ModBlocks.NEURAL_MOSS.get(), "Neural Moss");
        add(ModBlocks.CHARRED_FLESH.get(), "Charred Flesh");
        add(ModBlocks.LIVING_FLESH.get(), "Living Flesh");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Ossified Flesh");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Fireproof Flesh");
        add(ModBlocks.PULSING_HEART.get(), "Pulsing Heart");
        add(ModBlocks.HIVE_EYE.get(), "Hive Eye");
        add("entity.carnis.assimilated_player", "Assimilated %s");
        add("death.attack.organic_consumption", "%1$s was consumed by the hive");
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
        add("item.carnis.amalgam_bile_glob", "Amalgam Bile");
        add("entity.carnis.amalgam_bile", "Amalgam Bile");
        add("tooltip.carnis.amalgam_bile_glob", "A corrosive organic glob.");
        add("subtitles.carnis.amalgam_smash", "Amalgam slams the ground");
        add("subtitles.carnis.organic_creak", "Sinew lashes");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Flesh Amalgam Spawn Egg"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Purification Serum");
        add(ModItems.BIO_PURIFIER.get(), "Bio-Purifier");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Neuro-Resonator Helmet"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s was incinerated by a bio-purifier"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s was incinerated by %2$s's bio-purifier"
        );

        add("subtitles.carnis.phantom_creeper", "Something hisses behind you");
        add("subtitles.carnis.phantom_footsteps", "Footsteps squelch through flesh");
        add("subtitles.carnis.phantom_whisper", "The hivemind whispers");
        add("subtitles.carnis.pulsing_heart_beat", "A biome heart beats");
        add("subtitles.carnis.synapse_shock", "A synapse discharges");
        add("subtitles.carnis.synapse_rupture", "Nerve tissue tears apart");
        add("subtitles.carnis.digestor_churn", "A digestor churns");
        add("subtitles.carnis.hive_eye_screech", "The hive eye shrieks");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Flesh fuses into an amalgam"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "A projectile ricochets off bone"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Corrosive acid splashes"
        );
        add("subtitles.carnis.pustule_burst", "A pustule bursts");
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "The Flesh Amalgam groans"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "The Flesh Amalgam recoils"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "The Flesh Amalgam collapses"
        );
    }

    private void addRussianTranslations() {
        add("carnis.tab", "Carnis: Адаптивный коллективный разум");
        add("item.carnis.parasitic_tendril_spawn_egg", "Яйцо призыва: Паразитическое щупальце");
        add("tooltip.carnis.parasitic_tendril_spawn_egg", "Призывает существо: Паразитическое щупальце.");
        add("item.carnis.hive_sentinel_spawn_egg", "Яйцо призыва: Страж Улья");
        add("tooltip.carnis.hive_sentinel_spawn_egg", "Призывает существо: Страж Улья.");
        add("item.carnis.cerebral_nexus_spawn_egg", "Яйцо призыва: Мозговой Нексус");
        add("tooltip.carnis.cerebral_nexus_spawn_egg", "Призывает существо: Мозговой Нексус.");
        add("tooltip.carnis.biomass_remains", "Органические останки хозяина.");
        add("tooltip.carnis.flesh_bulb", "Созревающий органический мешок.");
        add("tooltip.carnis.sinew_spikes", "Колючие наросты замедляют существ.");
        add("tooltip.carnis.biomass_maggot_spawn_egg", "Призывает личинку биомассы.");
        add("codex.carnis.previous", "< Назад");
        add("codex.carnis.next", "Вперёд >");
        add("codex.carnis.tab.0", "Органогенез");
        add("codex.carnis.tab.1", "Биоценоз");
        add("codex.carnis.tab.2", "Аберрации");
        add("codex.carnis.tab.3", "Биотехнологии");
        add("codex.carnis.entry.0.title", "Пульсирующее сердце");
        add("codex.carnis.entry.0.body", "Центр колонии пульсирует каждые 100 тиков. Известная ему плоть и жилы дают меру роста в радиусе 32 блоков; сам импульс охватывает 8.");
        add("codex.carnis.entry.0.note", "Сердце считает лишь обнаруженную ткань.");
        add("codex.carnis.entry.1.title", "Порядок органов");
        add("codex.carnis.entry.1.body", "На 25, 50, 75 и 100 заражённых блоках улей закладывает око, стража, бассейн и столп. Для роста требуется живая плоть в 8–24 блоках.");
        add("codex.carnis.entry.1.note", "Орган растёт там, где клетка считает место пригодным.");
        add("codex.carnis.entry.2.title", "Око Улья");
        add("codex.carnis.entry.2.body", "Сенсор замечает чужаков в пределах 18 блоков и передаёт тревогу свободным мобам Улья в радиусе 28 блоков.");
        add("codex.carnis.entry.2.note", "Вопль слышен раньше, чем видно зрачок.");
        add("codex.carnis.entry.3.title", "Желудочный бассейн");
        add("codex.carnis.entry.3.body", "Кислота разлагает предметы и живую ткань. Погибший в ней скот отдаёт ближайшему сердцу 20 единиц биомассы, корова — 30.");
        add("codex.carnis.entry.3.note", "Пять единиц урона в секунду — достаточно, чтобы не входить.");
        add("codex.carnis.entry.4.title", "Нервный столп");
        add("codex.carnis.entry.4.body", "Столп рассеивает новый термический шок в радиусе 32 блоков. Щит сокращает поджог форм Улья, но не делает плоть несгораемой.");
        add("codex.carnis.entry.4.note", "Сначала разрушить якорь. Затем очистить очаг.");
        add("codex.carnis.entry.5.title", "Страж и Нексус");
        add("codex.carnis.entry.5.body", "Пси-якорь вводит скот в транс и ведёт его к бассейну. При четырёх органах и 200 единицах сердце может стать Мозговым Нексусом.");
        add("codex.carnis.entry.5.note", "Два дочерних сердца возникают на известной плоти в 48–64 блоках.");
        add("codex.carnis.entry.6.title", "Остатки биомассы");
        add("codex.carnis.entry.6.body", "На твёрдом полу гибель хозяина оставляет рыхлые останки. Они замедляют и чужаков, и существ Улья; близ падали появляются личинки.");
        add("codex.carnis.entry.6.note", "В воде и без опоры образец получить не удалось.");
        add("codex.carnis.entry.7.title", "Личинка биомассы");
        add("codex.carnis.entry.7.body", "Личинка ищет останки в радиусе 16 блоков. Два приёма пищи пробуждают инстинкт зарывания; час на плоти не требуется — достаточно минуты.");
        add("codex.carnis.entry.7.note", "Она выбирает рыхлую землю или плоть, но не камень.");
        add("codex.carnis.entry.8.title", "Кокон созревания");
        add("codex.carnis.entry.8.body", "Мясная луковица держится на потолке или на полу. Через 60–90 секунд её сердцебиение учащается, мешок лопается и выпускает щупальца.");
        add("codex.carnis.entry.8.note", "Счёт идёт только в загруженной области.");
        add("codex.carnis.entry.9.title", "Щупальце: внедрение");
        add("codex.carnis.entry.9.body", "При контакте вероятность заражения мирного хозяина — 85%, монстра — 45%; броня снижает шанс монстра до 30%. Паразит исчезает после броска.");
        add("codex.carnis.entry.9.note", "Провал сопровождается шипением и слабым ранением.");
        add("codex.carnis.entry.10.title", "Четыре стадии");
        add("codex.carnis.entry.10.body", "До 10 секунд — инкубация; до 25 — вены и опухоли; до 30 — разрыв и заражение почвы. Затем монстр мутирует, а мирный хозяин разлагается.");
        add("codex.carnis.entry.10.note", "На третьей стадии рана способна убить до превращения.");
        add("codex.carnis.entry.11.title", "Заражённый зомби");
        add("codex.carnis.entry.11.body", "Правая рука разрослась в костяной клинок; жгутики обрамляют разорванную голову. У останков он замирает и поглощает биомассу.");
        add("codex.carnis.entry.11.note", "Во время питания его взгляд удерживается на одном направлении.");
        add("codex.carnis.entry.12.title", "Заражённый скелет");
        add("codex.carnis.entry.12.body", "Костяной серп заменяет оружие. Проросший нерв и ядро в рёбрах излучают красный свет; удар лезвием может задеть соседние цели.");
        add("codex.carnis.entry.12.note", "Не принимать пустую глазницу за отсутствие зрения.");
        add("codex.carnis.entry.13.title", "Заражённый крипер");
        add("codex.carnis.entry.13.body", "Раздутые мешки колышутся до разрыва. Вместо обычного взрыва он выбрасывает споры, травит живых и оставляет жилы на прочных гранях.");
        add("codex.carnis.entry.13.note", "Признак детонации — бешеное дрожание нервных усиков.");
        add("codex.carnis.entry.14.title", "Амальгама плоти");
        add("codex.carnis.entry.14.body", "Титанический симбиот возникает из слияния заражённых форм у сердца. Костяные пластины и кислота меняются вместе с адаптацией Улья.");
        add("codex.carnis.entry.14.note", "Ослабленная амальгама поглощает останки и малые формы; берегитесь ударной волны и едкой желчи.");
        add("codex.carnis.entry.15.title", "Пневмоинокулятор");
        add("codex.carnis.entry.15.body", "Дротик несёт вирусный штамм или очищающий состав. На расстоянии учитывайте падение снаряда и укрытия; магазин расходует подходящие дротики.");
        add("codex.carnis.entry.15.note", "Очищающий состав снижает заражение игрока на 35.");
        add("codex.carnis.entry.16.title", "Био-очиститель");
        add("codex.carnis.entry.16.body", "Поток огня стерилизует живую и окостеневшую плоть, оставляя обугленную ткань. Термический удар обычно вызывает шок заражённого участка.");
        add("codex.carnis.entry.16.note", "Действующий нервный столп блокирует новый термошок.");
        add("codex.carnis.entry.17.title", "Нейро-броня");
        add("codex.carnis.entry.17.body", "Вплетённые сухожилия связывают доспех с нервной системой носителя. Каждая защищённая часть уменьшает заражающую экспозицию на четверть.");
        add("codex.carnis.entry.17.note", "Полный комплект скрывает носителя от Ока, но не обещает невидимости всем.");
        add("entity.carnis.hive_sentinel", "Страж Улья");
        add("entity.carnis.cerebral_nexus", "Мозговой узел");
        add("subtitles.carnis.inoculator_fire", "Выстрел инокулятора");
        add("subtitles.carnis.dart_hit", "Дротик ударяется");
        add("tooltip.carnis.flesh_bulb.mechanics", "Инкубационный мешок, способный закрепляться на потолке и полу.");
        add("tooltip.carnis.flesh_bulb.lore", "Внутри слышно глухое, частое сердцебиение зреющего выводка.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Наносят колющий урон и замедляют любое наступившее существо.");
        add("tooltip.carnis.sinew_spikes.lore", "Натянутые жилы реагируют на малейшую вибрацию шагов.");
        add("tooltip.carnis.biomass_maggot.mechanics", "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.");
        add("tooltip.carnis.biomass_maggot.lore", "Начальное звено паразитического круговорота Улья.");
        add("item.carnis.infected_zombie_spawn_egg", "Яйцо призыва заражённого зомби");
        add("entity.carnis.infected_zombie", "Заражённый зомби");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Призывает заражённого зомби.");
        add("item.carnis.antibiotics", "Антибиотики");
        add("effect.carnis.immunosuppression", "Иммуносупрессия");
        add("tooltip.carnis.antibiotics", "Предотвращает заражение на 3 минуты.");
        add("entity.carnis.parasitic_tendril", "Паразитический усик");
        add("effect.carnis.incubating", "Инкубация");
        add("subtitles.carnis.flamethrower_fire", "Огнемёт ревёт");
        add("subtitles.carnis.amalgam_roar", "Амальгама ревёт");
        add("codex.carnis.chapter.0", "Истоки и биомы");
        add("codex.carnis.body.0", "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.");
        add("codex.carnis.chapter.1", "Адаптивный разум");
        add("codex.carnis.body.1", "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.");
        add("codex.carnis.chapter.2", "Органы и флора улья");
        add("codex.carnis.body.2", "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.");
        add("codex.carnis.chapter.3", "Медицина и нейроплетение");
        add("codex.carnis.body.3", "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.");
        add("codex.carnis.chapter.4", "Мутанты и слияние");
        add("codex.carnis.body.4", "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.");
        add("entity.carnis.flesh_spat", "Плевок плоти");
        add("item.carnis.flesh_spat", "Плевок плоти");
        add("tooltip.carnis.flesh_spat", "Сгусток заражённой ткани.");
        add("subtitles.carnis.heartbeat_loop", "Сердце бьётся");
        add("item.carnis.research_journal", "Кодекс Карнис");
        add("tooltip.carnis.research_journal", "Полевой справочник по улью.");
        add("item.carnis.tainted_sludge_bucket", "Ведро заражённой слизи");
        add("item.carnis.bone_scythe_arm", "Костяная коса-рука");
        add("block.carnis.tainted_sludge", "Заражённая слизь");
        add("fluid_type.carnis.tainted_sludge", "Заражённая слизь");
        add("tooltip.carnis.tainted_sludge_bucket", "Ведро заразной слизи.");
        add("tooltip.carnis.bone_scythe_arm", "Зазубренный костяной клинок.");
        add("subtitles.carnis.amalgam_step", "Плотяная амальгама чавкает");
        add("block.carnis.flesh_veins", "Плотяные жилы");
        add("tooltip.carnis.flesh_veins", "Органические жилы на открытых поверхностях.");

        add("entity.carnis.infected_skeleton", "Заражённый скелет");
        add("item.carnis.infected_skeleton_spawn_egg", "Яйцо призыва: Заражённый скелет");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Призывает заражённого скелета.");
        add("entity.carnis.infected_creeper", "Заражённый крипер");
        add("item.carnis.infected_creeper_spawn_egg", "Яйцо призыва: Заражённый крипер");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Призывает заражённого крипера.");
        add("entity.carnis.infected_spider", "Заражённый паук");
        add("item.carnis.infected_spider_spawn_egg", "Яйцо призыва: Заражённый паук");
        add("tooltip.carnis.infected_spider_spawn_egg", "Призывает заражённого паука.");
        add("item.carnis.neuro_resonator_chestplate", "Нейро-резонаторный нагрудник");
        add("item.carnis.neuro_resonator_leggings", "Нейро-резонаторные поножи");
        add("item.carnis.neuro_resonator_boots", "Нейро-резонаторные ботинки");
        add("block.carnis.flesh_bulb", "Мясная луковица");
        add("block.carnis.biomass_remains", "Останки биомассы");
        add("block.carnis.sinew_spikes", "Сухожильные шипы");
        add("entity.carnis.biomass_maggot", "Личинка биомассы");
        add("item.carnis.biomass_maggot_spawn_egg", "Яйцо призыва: Личинка биомассы");
        add("item.carnis.neural_binding_matrix", "Матрица нейронного сплетения");
        add("tooltip.carnis.neuro_resonator_chestplate", "Биологический нагрудник снижает заражение.");
        add("tooltip.carnis.neuro_resonator_leggings", "Биологические поножи снижают заражение.");
        add("tooltip.carnis.neuro_resonator_boots", "Биологические ботинки снижают заражение.");
        add("tooltip.carnis.neural_binding_matrix", "Вплетите в броню на наковальне за пять уровней.");
        add("block.carnis.nerve_pillar", "Нервный столп");
        add("item.carnis.pneumatic_inoculator", "Пневматический инокулятор");
        add("item.carnis.viral_dart", "Вирусный дротик");
        add("item.carnis.purification_dart", "Очищающий дротик");
        add("entity.carnis.viral_dart", "Вирусный дротик");
        add("entity.carnis.purification_dart", "Очищающий дротик");
        add("death.attack.carnis_tainted_sludge", "%1$s растворился в заражённой жиже");
        add("death.attack.purification_dart", "%1$s очищен дротиком");
        add("death.attack.purification_dart.player", "%1$s очищен игроком %2$s");
        add("tooltip.carnis.nerve_pillar", "При установке вдвое сокращает оставшийся шок чанка.");
        add("tooltip.carnis.pneumatic_inoculator", "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.");
        add("tooltip.carnis.viral_dart", "Добавляет игрокам 25 заражения и вызывает слабость.");
        add("tooltip.carnis.purification_dart.mechanics", "Игрок: −35 заражения; снимает тошноту, слепоту и замедление.");
        add("tooltip.carnis.purification_dart.protocol", "Обращает мутацию гуманоидов; ранит и оглушает крупные организмы Улья.");
        add("tooltip.carnis.viral_dart.mechanics", "Игрок: +25 заражения и слабость.");
        add("tooltip.carnis.viral_dart.protocol", "Ускоряет инкубацию скота; мутирует зомби, скелетов и криперов.");
        add("tooltip.carnis.dart.use", "Зарядите пневматический инокулятор и выстрелите в цель.");
        add("subtitles.carnis.hive_alarm", "Око Улья кричит");
        add("subtitles.carnis.hive_ambient_drone", "Улей дышит");
        add("subtitles.carnis.creeper_rupture", "Биологический разрыв");
        add("entity.carnis.hive_spore_cloud", "Споровое облако Улья");
        add("tooltip.carnis.purification_serum.mechanics", "Выпейте, чтобы снять 35 очков заражения.");
        add("tooltip.carnis.purification_serum.use", "Выпейте напрямую или изготовьте дротики очищения.");
        add("entity.carnis.inoculator_dart", "Дротик инокулятора");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.neural_moss.mechanics", "Замедляет чужаков; растёт у воды и тканей Улья.");
        add("tooltip.carnis.neural_moss.lore", "Живой ковёр прислушивается к чужим шагам.");
        add("tooltip.carnis.creeping_tendrils", "Взбирайтесь по усикам на поверхности плоти.");
        add("tooltip.carnis.pustule_cluster", "Наступите без приседания: пустулы лопнут и заразят вас.");
        add("tooltip.carnis.stomach_pool", "Едкая ткань растворяет предметы в биомассу.");
        add("tooltip.carnis.ossified_flesh", "Окостеневшая ткань распространяет улей.");
        add("tooltip.carnis.fireproof_flesh", "Ткань, приспособленная к огню.");
        add("tooltip.carnis.veins", "Живые вены несут инфекцию через древесину.");
        add("tooltip.carnis.pulsing_heart", "Сердце улья ускоряет заражение поблизости.");
        add("tooltip.carnis.hive_eye", "Обнаруживает чужаков и тревожит ближайших существ Улья.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Призывает амальгаму плоти.");
        add("tooltip.carnis.purification_serum", "Выпейте, чтобы снизить заражение на 35 пунктов.");
        add("effect.carnis.thermal_shock", "Термический шок");
        add("subtitles.carnis.purifier_ignite", "Очиститель зажигается");
        add("subtitles.carnis.purifier_loop", "Очиститель выпускает пламя");
        add("tooltip.carnis.bio_purifier", "Удерживайте: конус пламени на 6,5 блока.");
        add("tooltip.carnis.neuro_resonator_helmet", "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.");
        add("itemGroup.carnis", "Carnis: Адаптивный коллективный разум");

        add("death.attack.necrotic_consumption", "%1$s поглощён коллективным разумом");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Ползучие щупальца");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Скопление пустул");
        add(ModBlocks.STOMACH_POOL.get(), "Желудочный бассейн");
        add(ModBlocks.SPORE_SPROUT.get(), "Споровый росток");
        add(ModBlocks.NEURAL_MOSS.get(), "Нервный мох");
        add(ModBlocks.CHARRED_FLESH.get(), "Обугленная плоть");
        add(ModBlocks.LIVING_FLESH.get(), "Живая плоть");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Окостенелая плоть");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Огнеупорная плоть");
        add(ModBlocks.PULSING_HEART.get(), "Сердце биома");
        add(ModBlocks.HIVE_EYE.get(), "Око разума");
        add("entity.carnis.assimilated_player", "Ассимилированный %s");
        add("death.attack.organic_consumption", "%1$s был поглощён Ульем");
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
        add("item.carnis.amalgam_bile_glob", "Желчь амальгамы");
        add("entity.carnis.amalgam_bile", "Желчь амальгамы");
        add("tooltip.carnis.amalgam_bile_glob", "Едкий органический сгусток.");
        add("subtitles.carnis.amalgam_smash", "Амальгама сотрясает землю");
        add("subtitles.carnis.organic_creak", "Сухожилие хлещет");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Яйцо призыва амальгамы плоти"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Очищающая сыворотка");
        add(ModItems.BIO_PURIFIER.get(), "Очищающий огнемёт");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Нейро-резонаторный шлем"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s сожжён биоочистителем"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s сожжён биоочистителем игрока %2$s"
        );

        add("subtitles.carnis.phantom_creeper", "Что-то шипит за спиной");
        add("subtitles.carnis.phantom_footsteps", "Шаги хлюпают по плоти");
        add("subtitles.carnis.phantom_whisper", "Коллективный разум шепчет");
        add("subtitles.carnis.pulsing_heart_beat", "Сердце биома бьётся");
        add("subtitles.carnis.synapse_shock", "Нервный столб разряжается");
        add("subtitles.carnis.synapse_rupture", "Нервная ткань разрывается");
        add("subtitles.carnis.digestor_churn", "Желудочный пруд бурлит");
        add("subtitles.carnis.hive_eye_screech", "Око разума визжит");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Плоть сливается в амальгаму"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "Снаряд рикошетит от кости"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Едкая кислота брызжет"
        );
        add("subtitles.carnis.pustule_burst", "Пустула лопается");
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "Амальгама плоти стонет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "Амальгама плоти вздрагивает"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "Амальгама плоти обрушивается"
        );
    }
}
