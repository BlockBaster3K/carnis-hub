package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, CarnisMod.MOD_ID);

    public static final RegistryObject<SoundEvent> INOCULATOR_FIRE =
            registerVariableRangeSound("item.inoculator.fire");
    public static final RegistryObject<SoundEvent> DART_HIT =
            registerVariableRangeSound("entity.dart.hit");

    public static final RegistryObject<SoundEvent> PURIFIER_IGNITE = registerVariableRangeSound("item.purifier.ignite");
    public static final RegistryObject<SoundEvent> PURIFIER_LOOP = registerVariableRangeSound("item.purifier.loop");
    public static final RegistryObject<SoundEvent> FLAMETHROWER_FIRE = registerVariableRangeSound("flamethrower_fire");
    public static final RegistryObject<SoundEvent> AMALGAM_SMASH = registerVariableRangeSound("amalgam_smash");
    public static final RegistryObject<SoundEvent> ORGANIC_CREAK = registerVariableRangeSound("organic_creak");
    public static final RegistryObject<SoundEvent> AMALGAM_ROAR = registerVariableRangeSound("amalgam_roar");

    public static final RegistryObject<SoundEvent> HEARTBEAT_LOOP = registerVariableRangeSound("heartbeat_loop");
    public static final RegistryObject<SoundEvent> HIVE_HEARTBEAT = registerVariableRangeSound("hive.heartbeat");

    public static final RegistryObject<SoundEvent> AMALGAM_STEP = registerVariableRangeSound("amalgam_step");

    public static final RegistryObject<SoundEvent> PHANTOM_CREEPER =
            registerVariableRangeSound("phantom_creeper");

    public static final RegistryObject<SoundEvent> PHANTOM_FOOTSTEPS =
            registerVariableRangeSound("phantom_footsteps");

    public static final RegistryObject<SoundEvent> PHANTOM_WHISPER =
            registerVariableRangeSound("phantom_whisper");

    public static final RegistryObject<SoundEvent> PULSING_HEART_BEAT =
            registerVariableRangeSound("pulsing_heart_beat");

    public static final RegistryObject<SoundEvent> SYNAPSE_SHOCK =
            registerVariableRangeSound("synapse_shock");

    public static final RegistryObject<SoundEvent> SYNAPSE_RUPTURE =
            registerVariableRangeSound("synapse_rupture");

    public static final RegistryObject<SoundEvent> DIGESTOR_CHURN =
            registerVariableRangeSound("digestor_churn");

    public static final RegistryObject<SoundEvent> HIVE_EYE_SCREECH =
            registerVariableRangeSound("hive.eye_screech");
    public static final RegistryObject<SoundEvent> HIVE_ALARM =
            registerVariableRangeSound("hive.alarm");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT =
            registerVariableRangeSound("hive.ambient");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_CLOSE =
            registerVariableRangeSound("hive.ambient_close");
    public static final RegistryObject<SoundEvent> HIVE_PULSE =
            registerVariableRangeSound("hive.pulse");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_TONAL_STINGER =
            registerVariableRangeSound("hive.ambient_tonal_stinger");

    public static final RegistryObject<SoundEvent> HIVE_AMB_SURFACE =
            registerVariableRangeSound("hive.ambient_surface");
    public static final RegistryObject<SoundEvent> HIVE_AMB_DEEP =
            registerVariableRangeSound("hive.ambient_deep");
    public static final RegistryObject<SoundEvent> HIVE_AMB_CORE =
            registerVariableRangeSound("hive.ambient_core");
    public static final RegistryObject<SoundEvent> HIVE_AMB_THRESHOLD =
            registerVariableRangeSound("hive.ambient_threshold");

    public static final RegistryObject<SoundEvent> ZONE_STINGER_INTENSIFY =
            registerVariableRangeSound("hive.zone_stinger_intensify");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_RELEASE =
            registerVariableRangeSound("hive.zone_stinger_release");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_DEEP =
            registerVariableRangeSound("hive.zone_stinger_deep");

    public static final RegistryObject<SoundEvent> FLESH_BLOCK_STEP =
            registerVariableRangeSound("flesh_block_step");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_PLACE =
            registerVariableRangeSound("hive.block_place");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_BREAK =
            registerVariableRangeSound("hive.block_break");
    public static final RegistryObject<SoundEvent> HIVE_SPREAD =
            registerVariableRangeSound("hive.spread");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT =
            registerVariableRangeSound("combat.flesh_hit");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT_DEEP =
            registerVariableRangeSound("combat.flesh_hit_deep");
    public static final RegistryObject<SoundEvent> COMBAT_DISMEMBER =
            registerVariableRangeSound("combat.dismember");
    public static final RegistryObject<SoundEvent> COMBAT_ARMOR_DEFLECT =
            registerVariableRangeSound("combat.armor_deflect");
    public static final RegistryObject<SoundEvent> COMBAT_BLOCK_STAB =
            registerVariableRangeSound("combat.block_stab");

    public static final RegistryObject<SoundEvent> HIVE_DETAIL_FLOW =
            registerVariableRangeSound("hive.detail_flow");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_MEMBRANE =
            registerVariableRangeSound("hive.detail_membrane");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_BUBBLES =
            registerVariableRangeSound("hive.detail_bubbles");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_CREAK =
            registerVariableRangeSound("hive.detail_creak");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_SCUTTLE =
            registerVariableRangeSound("hive.detail_scuttle");

    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ALERT =
            registerVariableRangeSound("hive.spawn_alert");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ATTACK =
            registerVariableRangeSound("hive.spawn_attack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_IDLE =
            registerVariableRangeSound("hive.spawn_idle");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT =
            registerVariableRangeSound("hive.spawn_hurt");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT_CRITICAL =
            registerVariableRangeSound("hive.spawn_hurt_critical");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_WHIP =
            registerVariableRangeSound("hive.spawn_skeleton_whip");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BLADE =
            registerVariableRangeSound("hive.spawn_skeleton_blade");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BONECRACK =
            registerVariableRangeSound("hive.spawn_skeleton_bonecrack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_SAC =
            registerVariableRangeSound("hive.spawn_creeper_sac");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_CRAWL =
            registerVariableRangeSound("hive.spawn_creeper_crawl");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_DETONATE =
            registerVariableRangeSound("hive.spawn_creeper_detonate");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SHUFFLE =
            registerVariableRangeSound("hive.amalgam_shuffle");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_BREATH =
            registerVariableRangeSound("hive.amalgam_breath");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SLAM =
            registerVariableRangeSound("hive.amalgam_slam");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_DEATH =
            registerVariableRangeSound("hive.spawn_death");

    public static final RegistryObject<SoundEvent> CREEPER_RUPTURE =
            registerVariableRangeSound("creeper_rupture");

    public static final RegistryObject<SoundEvent> AMALGAMATION_FUSE =
            registerVariableRangeSound("amalgamation_fuse");

    public static final RegistryObject<SoundEvent> BONE_DEFLECT =
            registerVariableRangeSound("bone_deflect");

    public static final RegistryObject<SoundEvent> ACID_SPLASH =
            registerVariableRangeSound("acid_splash");

    public static final RegistryObject<SoundEvent> PUSTULE_BURST =
            registerVariableRangeSound("pustule_burst");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_AMBIENT =
            registerVariableRangeSound("flesh_amalgam_ambient");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_HURT =
            registerVariableRangeSound("flesh_amalgam_hurt");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_DEATH =
            registerVariableRangeSound("flesh_amalgam_death");

    private ModSounds() {
    }

    private static RegistryObject<SoundEvent> registerVariableRangeSound(String name) {
        ResourceLocation soundId = new ResourceLocation(CarnisMod.MOD_ID, name);
        return SOUND_EVENTS.register(
                name,
                () -> SoundEvent.createVariableRangeEvent(soundId)
        );
    }

    public static void register(IEventBus modEventBus) {
        SOUND_EVENTS.register(modEventBus);
    }
}
