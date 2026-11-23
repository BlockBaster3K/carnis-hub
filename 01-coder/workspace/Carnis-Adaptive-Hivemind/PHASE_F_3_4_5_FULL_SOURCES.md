# Carnis 3.4.5 — полные тексты затронутых файлов


## `src/main/resources/assets/carnis/animations/entity/infected_skeleton.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.infected_skeleton.idle": {
      "loop": true,
      "animation_length": 0.8,
      "bones": {
        "ribs": {
          "rotation": {
            "0.0": [
              0,
              0,
              -1
            ],
            "0.2": [
              1,
              0,
              1
            ],
            "0.4": [
              0,
              0,
              -1
            ],
            "0.6": [
              -1,
              0,
              1
            ],
            "0.8": [
              0,
              0,
              -1
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              1
            ],
            "0.4": [
              0,
              0,
              -1
            ],
            "0.8": [
              0,
              0,
              1
            ]
          }
        },
        "neural_filaments": {
          "rotation": {
            "0.0": [
              0,
              0,
              -3
            ],
            "0.4": [
              4,
              0,
              4
            ],
            "0.8": [
              0,
              0,
              -3
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.walk": {
      "loop": true,
      "animation_length": 0.4,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              8,
              0,
              -4
            ],
            "0.1": [
              10,
              0,
              2
            ],
            "0.2": [
              8,
              0,
              4
            ],
            "0.3": [
              10,
              0,
              -2
            ],
            "0.4": [
              8,
              0,
              -4
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              -3,
              0,
              3
            ],
            "0.2": [
              -3,
              0,
              -3
            ],
            "0.4": [
              -3,
              0,
              3
            ]
          }
        },
        "left_leg": {
          "rotation": {
            "0.0": [
              40,
              0,
              0
            ],
            "0.2": [
              -40,
              0,
              0
            ],
            "0.4": [
              40,
              0,
              0
            ]
          }
        },
        "right_leg": {
          "rotation": {
            "0.0": [
              -40,
              0,
              0
            ],
            "0.2": [
              40,
              0,
              0
            ],
            "0.4": [
              -40,
              0,
              0
            ]
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": [
              -25,
              0,
              0
            ],
            "0.2": [
              25,
              0,
              0
            ],
            "0.4": [
              -25,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              25,
              0,
              0
            ],
            "0.2": [
              -25,
              0,
              0
            ],
            "0.4": [
              25,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.attack_scythe": {
      "loop": false,
      "animation_length": 0.65,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            ".18": [
              0,
              -24,
              -6
            ],
            ".38": [
              0,
              28,
              5
            ],
            ".65": [
              0,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            ".18": [
              -70,
              -30,
              -35
            ],
            ".38": [
              20,
              45,
              25
            ],
            ".65": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.attack_whip": {
      "loop": false,
      "animation_length": 0.45,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.1": [
              0,
              -12,
              -4
            ],
            "0.22": [
              0,
              16,
              4
            ],
            "0.45": [
              0,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.1": [
              -35,
              0,
              -15
            ],
            "0.22": [
              -15,
              0,
              -35
            ],
            "0.45": [
              0,
              0,
              0
            ]
          },
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.1": [
              1,
              1.2,
              1
            ],
            "0.22": [
              1,
              2.8,
              1
            ],
            "0.3": [
              1,
              1.4,
              1
            ],
            "0.45": [
              1,
              1,
              1
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.hurt": {
      "loop": false,
      "animation_length": 0.35,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.08": [
              -8,
              0,
              5
            ],
            "0.2": [
              5,
              0,
              -3
            ],
            "0.35": [
              0,
              0,
              0
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.08": [
              -7,
              0,
              8
            ],
            "0.35": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.death": {
      "loop": false,
      "animation_length": 1.0,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.4": [
              25,
              0,
              8
            ],
            "1.0": [
              80,
              0,
              35
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.5": [
              10,
              0,
              -8
            ],
            "1.0": [
              20,
              0,
              -15
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.35": [
              -40,
              0,
              -25
            ],
            "1.0": [
              -75,
              0,
              -45
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.bone_rattle": {
      "loop": true,
      "animation_length": 0.6,
      "bones": {
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              -3
            ],
            "0.15": [
              3,
              0,
              3
            ],
            "0.3": [
              -2,
              0,
              -2
            ],
            "0.45": [
              2,
              0,
              3
            ],
            "0.6": [
              0,
              0,
              -3
            ]
          }
        },
        "ribs": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.3": [
              1,
              0,
              1
            ],
            "0.6": [
              0,
              0,
              0
            ]
          }
        }
      }
    }
  }
}
```


## `src/main/java/com/carnis/mod/entity/BiomassValued.java`

```java
package com.carnis.mod.entity;

/** Exposes an entity's explicit biomass value where the caller needs one. */
public interface BiomassValued {
    long getBiomassValue();
}
```


## `src/main/java/com/carnis/mod/entity/HiveEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Common base for living hive monsters; keeps shared sound and critical-wound behavior centralized. */
public abstract class HiveEntity extends Monster implements BiomassValued {
    private static final String CRITICAL_HURT_COOLDOWN = "carnis:hive_critical_hurt_ms";
    private static final long CRITICAL_HURT_COOLDOWN_MS = 120L;

    protected HiveEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public static net.minecraft.world.entity.ai.attributes.AttributeSupplier.Builder createAttributes() {
        return HiveEntityAttributes.create();
    }

    // Явное значение биомассы. Множители НЕ применяются.
    @Override
    public long getBiomassValue() {
        return 0L;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HIVE_SPAWN_DEATH.get();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide && isAlive() && getMaxHealth() > 0.0F
                && getHealth() / getMaxHealth() < 0.25F) {
            long now = System.currentTimeMillis();
            long last = getPersistentData().getLong(CRITICAL_HURT_COOLDOWN);
            if (now - last >= CRITICAL_HURT_COOLDOWN_MS) {
                getPersistentData().putLong(CRITICAL_HURT_COOLDOWN, now);
                level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_HURT_CRITICAL.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
            }
        }
        return hurt;
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedCreeperEntity extends Creeper implements HivemindLinkedMob, AssimilatingMob, GeoEntity, BiomassValued {
    private static final long BIOMASS_VALUE = 8L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_creeper.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_creeper.walk");
    private static final RawAnimation FUSE = RawAnimation.begin().thenLoop("animation.infected_creeper.fuse");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_creeper.assimilate");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedCreeperEntity(EntityType<? extends Creeper> type, Level level) { super(type, level); }

    @Override protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }
    @Override public long getBiomassValue() { return BIOMASS_VALUE; }
    @Override public boolean isAssimilating() { return entityData.get(ASSIMILATING); }
    @Override public void setAssimilating(boolean value) { entityData.set(ASSIMILATING, value); }

    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2, state ->
                state.setAndContinue(getSwellDir() > 0 || isIgnited() ? FUSE
                        : isAssimilating() ? ASSIMILATE : state.isMoving() ? WALK : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override protected void registerGoals() {
        super.registerGoals();
        goalSelector.addGoal(7, new CarnisFeedingGoal(this));
        goalSelector.addGoal(8, new CarnisGestationGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }
    public static AttributeSupplier.Builder createAttributes() {
        return Creeper.createAttributes().add(Attributes.MAX_HEALTH, 24.0D);
    }

    private boolean ruptured;

    /** Replaces the canceled vanilla explosion; the event listener guarantees server authority. */
    public void rupture(ServerLevel level) {
        if (ruptured) return;
        ruptured = true;
        double radius = 4.5D;
        level.playSound(null, blockPosition(), ModSounds.CREEPER_RUPTURE.get(), SoundSource.HOSTILE, 2F, 1.0F);
        level.sendParticles(ParticleTypes.SNEEZE, getX(), getY() + .7D, getZ(), 100, .7D, .6D, .7D, .16D);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY() + .7D, getZ(), 90, .7D, .6D, .7D, .18D);
        level.sendParticles(ParticleTypes.CRIMSON_SPORE, getX(), getY() + .8D, getZ(), 70, .9D, .6D, .9D, .1D);
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class,
                getBoundingBox().inflate(radius), e -> e != this && e.isAlive() && !e.isSpectator()
                        && e.distanceToSqr(this) <= radius * radius)) {
            target.hurt(level.damageSources().mobAttack(this), 12F);
            if (target.isAlive()) target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
        }
        HiveSporeCloudEntity cloud = com.carnis.mod.init.ModEntities.HIVE_SPORE_CLOUD.get().create(level);
        if (cloud != null) {
            cloud.setPos(getX(), getY(), getZ());
            cloud.setOwner(this);
            cloud.setRadius(3.0F);
            cloud.setWaitTime(0);
            cloud.setDuration(160);
            cloud.setRadiusPerTick(0F);
            cloud.setRadiusOnUse(0F);
            cloud.setDurationOnUse(0);
            cloud.setParticle(ParticleTypes.SNEEZE);
            cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
            cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 100, 0));
            level.addFreshEntity(cloud);
        }
        if (!ForgeEventFactory.getMobGriefingEvent(level, this)) return;
        BlockPos center = blockPosition();
        for (BlockPos mutable : BlockPos.betweenClosed(center.offset(-3, -3, -3), center.offset(3, 3, 3))) {
            BlockPos pos = mutable.immutable();
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)
                    || pos.distToCenterSqr(getX(), getY(), getZ()) > 9D) continue;
            BlockState existing = level.getBlockState(pos);
            boolean vein = existing.is(ModBlocks.FLESH_VEINS.get());
            if ((!vein && !existing.isAir()) || !existing.getFluidState().isEmpty()) continue;
            BlockState result = vein ? existing : Blocks.AIR.defaultBlockState();
            for (Direction face : Direction.values()) {
                BlockPos support = pos.relative(face);
                if (!level.hasChunkAt(support) || level.isOutsideBuildHeight(support)
                        || !level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(result, level, pos, face);
                if (next != null) result = next;
            }
            if (!result.equals(existing)) level.setBlockAndUpdate(pos, result);
        }
        if (level.random.nextFloat() >= .4F) return;
        for (BlockPos pos : new BlockPos[]{center, center.above(), center.below(), center.north(), center.south(), center.east(), center.west()}) {
            if (!level.hasChunkAt(pos) || !level.hasChunkAt(pos.below()) || level.isOutsideBuildHeight(pos)) continue;
            BlockState existing = level.getBlockState(pos);
            if (!existing.isAir() && !existing.is(ModBlocks.FLESH_VEINS.get())) continue;
            if (!existing.getFluidState().isEmpty()) continue;
            BlockState growth = (level.random.nextBoolean() ? ModBlocks.PUSTULE_CLUSTER.get() : ModBlocks.BIOMASS_REMAINS.get()).defaultBlockState();
            if (growth.canSurvive(level, pos) && level.setBlockAndUpdate(pos, growth)) break;
        }
    }
}
```


## `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.FleshAmalgamChargeGoal;
import com.carnis.mod.event.AcidAttackSlowdown;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class FleshAmalgamEntity extends HiveEntity
        implements GeoEntity, HivemindLinkedMob {
    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
        playSound(ModSounds.AMALGAM_STEP.get(), 0.9F, 1.0F);
    }

    private static final long BIOMASS_VALUE = 25L;

    public static final double MAX_HEALTH = 240.0D;
    public static final double KNOCKBACK_RESISTANCE = 1.0D;
    public static final double ATTACK_DAMAGE = 14.0D;
    public static final double MOVEMENT_SPEED = 0.22D;
    public static final double FOLLOW_RANGE = 32.0D;
    public static final double ARMOR = 12.0D;
    public static final double ARMOR_TOUGHNESS = 4.0D;

    public static final double CHARGE_TRIGGER_DISTANCE = 12.0D;

    private static final String REFLECTED_PROJECTILE_TAG =
            CarnisMod.MOD_ID + ":amalgam_reflected";

    private static final double PROJECTILE_REFLECTION_BASE_CHANCE = 0.06D;
    private static final double PROJECTILE_REFLECTION_CHANCE_PER_LEVEL = 0.0075D;
    private static final double PROJECTILE_REFLECTION_MAX_CHANCE = 0.45D;

    private static final double ACID_BASE_CHANCE = 0.08D;
    private static final double ACID_CHANCE_PER_LEVEL = 0.007D;
    private static final double ACID_MAX_CHANCE = 0.50D;
    private static final int ACID_BASE_ARMOR_DAMAGE = 2;
    private static final int ACID_MAX_ARMOR_DAMAGE = 6;
    private static final long ACID_LEVELS_PER_ARMOR_DAMAGE = 15L;
    private static final int ACID_BASE_DURATION_TICKS = 40;
    private static final int ACID_MAX_DURATION_TICKS = 100;
    private static final long ACID_EMPOWERED_SLOW_LEVEL = 50L;

    private static final double THORN_BASE_CHANCE = 0.08D;
    private static final double THORN_CHANCE_PER_LEVEL = 0.008D;
    private static final double THORN_MAX_CHANCE = 0.55D;
    private static final float THORN_BASE_DAMAGE = 1.5F;
    private static final float THORN_DAMAGE_PER_LEVEL = 0.05F;
    private static final float THORN_MAX_DAMAGE = 5.0F;

    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.idle");
    private static final RawAnimation WALK_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.walk");
    private static final RawAnimation ATTACK_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.attack");
    private static final RawAnimation SLAM_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.slam");
    private static final RawAnimation ROAR_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.roar");

    private final net.minecraft.server.level.ServerBossEvent bossBar = new net.minecraft.server.level.ServerBossEvent(
            getDisplayName(), net.minecraft.world.BossEvent.BossBarColor.RED,
            net.minecraft.world.BossEvent.BossBarOverlay.NOTCHED_10);
    private final com.carnis.mod.entity.ai.AmalgamBiomassFeast biomassFeast =
            new com.carnis.mod.entity.ai.AmalgamBiomassFeast(this);
    private long slamReady;
    private long pullReady;
    private long bileReady;
    private long feastReady;

    private final AnimatableInstanceCache animationCache =
            GeckoLibUtil.createInstanceCache(this);

    public FleshAmalgamEntity(
            EntityType<? extends FleshAmalgamEntity> entityType,
            Level level
    ) {
        super(entityType, level);
        this.xpReward = 18;
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, MAX_HEALTH)
                .add(Attributes.KNOCKBACK_RESISTANCE, KNOCKBACK_RESISTANCE)
                .add(Attributes.ATTACK_DAMAGE, ATTACK_DAMAGE)
                .add(Attributes.MOVEMENT_SPEED, MOVEMENT_SPEED)
                .add(Attributes.FOLLOW_RANGE, FOLLOW_RANGE)
                .add(Attributes.ARMOR, ARMOR)
                .add(Attributes.ARMOR_TOUGHNESS, ARMOR_TOUGHNESS);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new com.carnis.mod.entity.ai.FleshAmalgamAbilityGoal(this));
        goalSelector.addGoal(2, new FleshAmalgamChargeGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(
                5,
                new WaterAvoidingRandomStrollGoal(this, 0.8D)
        );
        goalSelector.addGoal(
                6,
                new LookAtPlayerGoal(this, Player.class, 10.0F)
        );
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));

        targetSelector.addGoal(
                1,
                new NearestAttackableTargetGoal<>(
                        this,
                        Player.class,
                        true,
                        target -> target instanceof Player player
                                && PlayerInfectionApi.isHostileTarget(player)
                )
        );
        targetSelector.addGoal(
                2,
                new HurtByTargetGoal(this).setAlertOthers()
        );
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (
                target instanceof Player player
                        && PlayerInfectionApi.isAssimilated(player)
        ) {
            return false;
        }

        return super.canAttack(target);
    }

    public boolean canUseAbility(int ability) {
        long now = level().getGameTime();
        return switch (ability) {
            case 1 -> now >= slamReady;
            case 2 -> now >= pullReady;
            case 3 -> now >= bileReady;
            default -> false;
        };
    }

    public void consumeAbilityCooldown(int ability) {
        long now = level().getGameTime();
        switch (ability) {
            case 1 -> slamReady = now + 160L;
            case 2 -> pullReady = now + 240L;
            case 3 -> bileReady = now + 200L;
            default -> throw new IllegalArgumentException("Unknown ability: " + ability);
        }
    }

    public long getFeastReady() { return feastReady; }
    public void setFeastReady(long tick) { feastReady = tick; }

    @Override
    public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel server)) return;
        if (!isAlive()) { bossBar.removeAllPlayers(); return; }
        bossBar.setProgress(net.minecraft.util.Mth.clamp(getHealth() / getMaxHealth(), 0.0F, 1.0F));
        bossBar.setName(getDisplayName());
        if (tickCount % 10 == 0) {
            for (ServerPlayer player : new java.util.ArrayList<>(bossBar.getPlayers())) {
                if (player.serverLevel() != server || !server.players().contains(player)
                        || !player.isAlive() || player.distanceToSqr(this) > 32.0D * 32.0D) bossBar.removePlayer(player);
            }
            for (ServerPlayer player : server.players()) {
                if (player.isAlive() && player.distanceToSqr(this) <= 32.0D * 32.0D) bossBar.addPlayer(player);
                else bossBar.removePlayer(player);
            }
        }
        if (!isNoAi()) biomassFeast.tick(server);
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        bossBar.removeAllPlayers();
        super.remove(reason);
    }

    @Override
    public void addAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putLong("CarnisSlamReady", slamReady);
        tag.putLong("CarnisPullReady", pullReady);
        tag.putLong("CarnisBileReady", bileReady);
        tag.putLong("CarnisFeastReady", feastReady);
    }

    @Override
    public void readAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        slamReady = tag.getLong("CarnisSlamReady");
        pullReady = tag.getLong("CarnisPullReady");
        bileReady = tag.getLong("CarnisBileReady");
        feastReady = tag.getLong("CarnisFeastReady");
    }

    @Override
    protected void customServerAiStep() {
        LivingEntity target = getTarget();

        if (
                target instanceof Player player
                        && PlayerInfectionApi.isAssimilated(player)
        ) {
            setTarget(null);
        }

        super.customServerAiStep();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return super.hurt(source, amount);
        }

        LivingEntity meleeAttacker = getDirectMeleeAttacker(source);
        boolean hurt = super.hurt(source, amount);

        if (hurt && meleeAttacker != null) {
            trySpikedRetaliation(serverLevel, meleeAttacker);
        }

        return hurt;
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);

        if (
                hit
                        && target instanceof ServerPlayer player
                        && level() instanceof ServerLevel serverLevel
        ) {
            tryAcidSplash(serverLevel, player);
        }

        return hit;
    }

    /**
     * Called from the Forge projectile-impact hook before vanilla processes
     * the collision. Returning true means the event must skip that impact.
     */
    public boolean tryDeflectProjectile(Projectile projectile) {
        if (
                !(level() instanceof ServerLevel serverLevel)
                        || projectile.isRemoved()
                        || !(projectile instanceof AbstractArrow)
                        || projectile.getOwner() == this
                        || projectile.getPersistentData().getBoolean(
                                REFLECTED_PROJECTILE_TAG
                        )
        ) {
            return false;
        }

        long rangedLevel = getAdaptationLevel(AdaptationType.RANGED);
        double reflectionChance = scaledChance(
                rangedLevel,
                PROJECTILE_REFLECTION_BASE_CHANCE,
                PROJECTILE_REFLECTION_CHANCE_PER_LEVEL,
                PROJECTILE_REFLECTION_MAX_CHANCE
        );

        if (
                reflectionChance <= 0.0D
                        || getRandom().nextDouble() >= reflectionChance
        ) {
            return false;
        }

        Vec3 incomingMovement = projectile.getDeltaMovement();
        Vec3 reflected = incomingMovement.scale(-0.4D).add(
                (getRandom().nextDouble() - 0.5D) * 0.2D,
                0.1D,
                (getRandom().nextDouble() - 0.5D) * 0.2D
        );
        projectile.getPersistentData().putBoolean(REFLECTED_PROJECTILE_TAG, true);
        projectile.setDeltaMovement(reflected);
        serverLevel.getChunkSource().broadcast(
                projectile, new ClientboundSetEntityMotionPacket(projectile)
        );
        Vec3 impactPosition = projectile.position();
        serverLevel.playSound(null, impactPosition.x, impactPosition.y, impactPosition.z,
                SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1.0F, 1.0F);
        playBoneDeflectEffects(serverLevel, impactPosition);
        return true;
    }

    public long getRangedAdaptationLevel() {
        return getAdaptationLevel(AdaptationType.RANGED);
    }

    private void tryAcidSplash(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double acidChance = scaledChance(
                meleeLevel,
                ACID_BASE_CHANCE,
                ACID_CHANCE_PER_LEVEL,
                ACID_MAX_CHANCE
        );

        if (
                acidChance <= 0.0D
                        || getRandom().nextDouble() >= acidChance
        ) {
            return;
        }

        int armorDamageBonus = (int) Math.min(
                ACID_MAX_ARMOR_DAMAGE - ACID_BASE_ARMOR_DAMAGE,
                meleeLevel / ACID_LEVELS_PER_ARMOR_DAMAGE
        );
        int armorDamage = ACID_BASE_ARMOR_DAMAGE + armorDamageBonus;

        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (!slot.isArmor()) {
                continue;
            }

            ItemStack armorStack = player.getItemBySlot(slot);

            if (!armorStack.isEmpty() && armorStack.isDamageableItem()) {
                armorStack.hurtAndBreak(
                        armorDamage,
                        player,
                        wearer -> wearer.broadcastBreakEvent(slot)
                );
            }
        }

        int duration = ACID_BASE_DURATION_TICKS + (int) Math.min(
                ACID_MAX_DURATION_TICKS - ACID_BASE_DURATION_TICKS,
                meleeLevel
        );
        AcidAttackSlowdown.apply(
                player,
                duration,
                meleeLevel >= ACID_EMPOWERED_SLOW_LEVEL
        );

        playAcidSplashEffects(serverLevel, player);
    }

    private void trySpikedRetaliation(
            ServerLevel serverLevel,
            LivingEntity attacker
    ) {
        if (!attacker.isAlive() || attacker == this) {
            return;
        }

        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double thornChance = scaledChance(
                meleeLevel,
                THORN_BASE_CHANCE,
                THORN_CHANCE_PER_LEVEL,
                THORN_MAX_CHANCE
        );

        if (
                thornChance <= 0.0D
                        || getRandom().nextDouble() >= thornChance
        ) {
            return;
        }

        float thornDamage = (float) Math.min(
                THORN_MAX_DAMAGE,
                THORN_BASE_DAMAGE + meleeLevel * THORN_DAMAGE_PER_LEVEL
        );

        if (attacker.hurt(serverLevel.damageSources().thorns(this), thornDamage)) {
            serverLevel.sendParticles(
                    ParticleTypes.CRIT,
                    attacker.getX(),
                    attacker.getY() + attacker.getBbHeight() * 0.6D,
                    attacker.getZ(),
                    18,
                    0.45D,
                    0.55D,
                    0.45D,
                    0.18D
            );
        }
    }

    private LivingEntity getDirectMeleeAttacker(DamageSource source) {
        if (
                source.is(DamageTypeTags.IS_FIRE)
                        || source.is(DamageTypeTags.IS_PROJECTILE)
                        || source.is(DamageTypeTags.IS_EXPLOSION)
                        || source.is(DamageTypes.THORNS)
                        || !(source.getEntity() instanceof LivingEntity attacker)
                        || source.getDirectEntity() != attacker
        ) {
            return null;
        }

        return attacker;
    }

    private void playBoneDeflectEffects(
            ServerLevel serverLevel,
            Vec3 impactPosition
    ) {
        serverLevel.playSound(
                null,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                ModSounds.BONE_DEFLECT.get(),
                SoundSource.HOSTILE,
                1.1F,
                1.0F
        );

        ItemParticleOption boneParticle = new ItemParticleOption(
                ParticleTypes.ITEM,
                new ItemStack(Items.BONE)
        );
        serverLevel.sendParticles(
                boneParticle,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                24,
                0.55D,
                0.65D,
                0.55D,
                0.16D
        );
        serverLevel.sendParticles(
                ParticleTypes.ELECTRIC_SPARK,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                18,
                0.48D,
                0.52D,
                0.48D,
                0.20D
        );
        serverLevel.sendParticles(
                ParticleTypes.CRIT,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                12,
                0.42D,
                0.48D,
                0.42D,
                0.14D
        );
    }

    private void playAcidSplashEffects(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        double effectY = player.getY() + player.getBbHeight() * 0.6D;
        serverLevel.playSound(
                null,
                player.getX(),
                effectY,
                player.getZ(),
                ModSounds.ACID_SPLASH.get(),
                SoundSource.HOSTILE,
                1.0F,
                1.0F
        );
        serverLevel.sendParticles(
                ParticleTypes.ITEM_SLIME,
                player.getX(),
                effectY,
                player.getZ(),
                32,
                0.55D,
                0.65D,
                0.55D,
                0.14D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPIT,
                player.getX(),
                effectY,
                player.getZ(),
                20,
                0.5D,
                0.6D,
                0.5D,
                0.12D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPLASH,
                player.getX(),
                effectY,
                player.getZ(),
                16,
                0.6D,
                0.55D,
                0.6D,
                0.10D
        );
    }

    private long getAdaptationLevel(AdaptationType type) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return 0L;
        }

        return CarnisWorldData.get(serverLevel).getAdaptation(type);
    }

    private static double scaledChance(
            long level,
            double baseChance,
            double chancePerLevel,
            double maximumChance
    ) {
        if (level <= 0L) {
            return 0.0D;
        }

        return Math.min(
                maximumChance,
                baseChance + level * chancePerLevel
        );
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!level().isClientSide) triggerAnim("roar_controller", "roar");
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.FLESH_AMALGAM_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource damageSource) {
        return ModSounds.FLESH_AMALGAM_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FLESH_AMALGAM_DEATH.get();
    }

    @Override
    public void registerControllers(
            AnimatableManager.ControllerRegistrar controllers
    ) {
        controllers.add(
                new AnimationController<>(
                        this,
                        "locomotion_controller",
                        5,
                        state -> state.setAndContinue(
                                state.isMoving()
                                        ? WALK_ANIMATION
                                        : IDLE_ANIMATION
                        )
                ),
                new AnimationController<>(
                        this,
                        "attack_controller",
                        2,
                        state -> {
                            if (swinging) {
                                return state.setAndContinue(ATTACK_ANIMATION);
                            }

                            state.getController().forceAnimationReset();
                            return PlayState.STOP;
                        }
                ),
                new AnimationController<>(this, "roar_controller", 2,
                        state -> PlayState.STOP).triggerableAnim("roar", ROAR_ANIMATION),
                new AnimationController<>(this, "slam_controller", 1,
                        state -> PlayState.STOP).triggerableAnim("slam", SLAM_ANIMATION)
        );
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
```


## `src/main/java/com/carnis/mod/entity/HiveSentinelEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.event.HypnosisEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class HiveSentinelEntity extends Monster implements GeoEntity, HivemindLinkedMob, BiomassValued {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.hive_sentinel.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private BlockPos heartPos;
    public HiveSentinelEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ARMOR, 8.0D).add(Attributes.KNOCKBACK_RESISTANCE, 1.0D).add(Attributes.MOVEMENT_SPEED, 0.0D);
    }
    @Override public long getBiomassValue() { return 40L; }
    public void setHeartPos(BlockPos pos) { heartPos = pos.immutable(); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() {
        super.tick();
        setDeltaMovement(0, 0, 0);
        if (!(level() instanceof ServerLevel server) || !isAlive() || tickCount % 20 != 0) return;
        if (tickCount % 100 == 0) server.playSound(null, blockPosition(), ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 0.9F, 1.0F);
        BlockPos pool = heartPos == null ? null : HiveNetwork.nearestLoaded(server, HiveNetwork.Kind.POOL, heartPos, 32);
        AABB area = getBoundingBox().inflate(16.0D);
        for (var animal : server.getEntitiesOfClass(net.minecraft.world.entity.animal.Animal.class, area,
                a -> (a instanceof Cow || a instanceof Sheep || a instanceof Pig) && a.isAlive()
                        && a.distanceToSqr(this) <= 256.0D && !InfectionHandler.isInfected(a))) {
            HypnosisEvents.apply(animal, server, pool);
        }
    }
    @Override public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (level() instanceof ServerLevel server && heartPos != null) {
            HiveNetwork.get(server).noteSentinelDeath(getUUID());
            if (server.hasChunkAt(heartPos) && server.getBlockEntity(heartPos) instanceof PulsingHeartBlockEntity heart)
                heart.sentinelDied(getUUID());
        }
        super.die(source);
    }
    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag); if (heartPos != null) tag.putLong("HiveHeart", heartPos.asLong());
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag); if (tag.contains("HiveHeart")) heartPos = BlockPos.of(tag.getLong("HiveHeart"));
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```


## `src/main/java/com/carnis/mod/entity/CerebralNexusEntity.java`

```java
package com.carnis.mod.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Tier-two command node; later tier mechanics are intentionally not defined here. */
public final class CerebralNexusEntity extends Monster implements GeoEntity, HivemindLinkedMob, BiomassValued {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long biomass;
    public CerebralNexusEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 120D).add(Attributes.ARMOR, 10D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1D).add(Attributes.MOVEMENT_SPEED, 0D);
    }
    @Override public long getBiomassValue() { return 100L; }
    public void setBiomass(long value) { biomass = Math.max(0L, value); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() { super.tick(); setDeltaMovement(0, 0, 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putLong("Biomass", biomass); }
    @Override public void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag); biomass = Math.max(0, tag.getLong("Biomass")); }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.cerebral_nexus.idle"))));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedZombieEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 3L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedZombieEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_zombie.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_zombie.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_zombie.assimilate");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.infected_zombie.pulsing");
    private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.infected_zombie.attack");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedZombieEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 3, state -> {
            if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
            return state.setAndContinue(state.isMoving() ? WALK : IDLE);
        }));
        controllers.add(new AnimationController<>(this, "pulsing", 0, state -> {
            if (isAssimilating()) return PlayState.STOP;
            return state.setAndContinue(PULSE);
        }));
        controllers.add(new AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(2, new CarnisFeedingGoal(this));
        goalSelector.addGoal(3, new CarnisGestationGoal(this));
        goalSelector.addGoal(4, new RandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(5, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 35.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.25D)
                .add(Attributes.FOLLOW_RANGE, 16.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.3D)
                .add(Attributes.ARMOR, 2.0D);
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_IDLE.get();
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        boolean success = super.doHurtTarget(target);
        if (success && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ATTACK.get(),
                    SoundSource.HOSTILE, 0.9F, 0.9F + random.nextFloat() * 0.2F);
        }
        return success;
    }

    @Override
    public void setTarget(LivingEntity target) {
        boolean wasUntargeted = getTarget() == null;
        super.setTarget(target);
        if (wasUntargeted && target != null && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ALERT.get(),
                    SoundSource.HOSTILE, 0.9F, 0.95F + random.nextFloat() * 0.1F);
        }
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedSpiderEntity.java`

```java
package com.carnis.mod.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.level.Level;

public final class InfectedSpiderEntity extends Spider implements HivemindLinkedMob, AssimilatingMob, software.bernie.geckolib.animatable.GeoEntity {
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> ASSIMILATING =
            net.minecraft.network.syncher.SynchedEntityData.defineId(InfectedSpiderEntity.class,
                    net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public boolean isAssimilating() { return entityData.get(ASSIMILATING); }

    @Override
    public void setAssimilating(boolean assimilating) { entityData.set(ASSIMILATING, assimilating); }

    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache geoCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override
    public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "movement", 3,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                        .thenLoop("animation.infected_spider." + (isAssimilating() ? "assimilate" : state.isMoving() ? "walk" : "idle")))));
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                    .thenPlay("animation.infected_spider.attack"));
            state.getController().forceAnimationReset();
            return software.bernie.geckolib.core.object.PlayState.STOP;
        }));
    }

    @Override
    public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    public InfectedSpiderEntity(EntityType<? extends Spider> type, Level level) {
        super(type, level);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        goalSelector.addGoal(7, new com.carnis.mod.entity.ai.CarnisFeedingGoal(this));
        goalSelector.addGoal(8, new com.carnis.mod.entity.ai.CarnisGestationGoal(this));
        targetSelector.addGoal(3, new com.carnis.mod.entity.ai.CarnisHuntPreyGoal(this));
        goalSelector.addGoal(9, new com.carnis.mod.entity.ai.InfectedSpiderRangedSpatGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Spider.createAttributes().add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D);
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedSkeletonEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 5L;
    private static final int WHIP_ANIMATION_TICKS = 9;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> WHIP_ANIM_TICKS =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.INT);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_skeleton.walk");
    private static final RawAnimation BONE_RATTLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.bone_rattle");
    private static final RawAnimation BLADE_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_scythe");
    private static final RawAnimation WHIP_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_whip");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedSkeletonEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(WHIP_ANIM_TICKS, 0);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    public boolean isWhipping() {
        return entityData.get(WHIP_ANIM_TICKS) > 0;
    }

    public void beginWhipAnimation() {
        entityData.set(WHIP_ANIM_TICKS, WHIP_ANIMATION_TICKS);
    }

    @Override
    public void tick() {
        if (!level().isClientSide) {
            int whipAnimTicks = entityData.get(WHIP_ANIM_TICKS);
            if (whipAnimTicks > 0) entityData.set(WHIP_ANIM_TICKS, whipAnimTicks - 1);
        }
        super.tick();
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 25.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 20.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.2D)
                .add(Attributes.ARMOR, 1.0D);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2, state -> {
            return state.setAndContinue(isAssimilating() ? BONE_RATTLE : state.isMoving() ? WALK : IDLE);
        }));
        controllers.add(new AnimationController<>(this, "action", 0, state -> {
            if (isWhipping()) return state.setAndContinue(WHIP_ATTACK);
            if (!isAssimilating() && swinging) return state.setAndContinue(BLADE_ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new InfectedSkeletonAttackGoal(this, 1.15D));
        goalSelector.addGoal(2, new MoveTowardsRestrictionGoal(this, 0.9D));
        goalSelector.addGoal(3, new WaterAvoidingRandomStrollGoal(this, 0.9D));
        goalSelector.addGoal(4, new LookAtPlayerGoal(this, Player.class, 10.0F));
        goalSelector.addGoal(5, new RandomLookAroundGoal(this));
        goalSelector.addGoal(6, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(7, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(8, new CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new CarnisGestationGoal(this));

        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        // This argument may be a candidate target not yet installed as getTarget().
        // Keep the eligibility check independent of range so target acquisition can start pursuit.
        return target != null && !target.isDeadOrDying()
                && !(target instanceof HiveEntity || target instanceof HivemindLinkedMob)
                && super.canAttack(target);
    }

    /** Immediate-hit checks are separate from target eligibility so out-of-range targets can be pursued. */
    private boolean canAttackNow(LivingEntity target) {
        if (!canAttack(target)) return false;
        Vec3 offset = target.position().subtract(position());
        Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
        if (offset.lengthSqr() > 9.0D || !hasLineOfSight(target)) return false;
        if (horizontal.lengthSqr() < 1.0E-8D) return true;

        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }
        return forward.dot(horizontal.normalize()) >= -0.15D;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && (target instanceof HiveEntity || target instanceof HivemindLinkedMob)) return;
        super.setTarget(target);
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        if (!(target instanceof LivingEntity livingTarget) || !canAttackNow(livingTarget)) return false;
        boolean hit = super.doHurtTarget(target);
        if (hit && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_BLADE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        return hit;
    }

    /** Resolve the wide 3-block lash; damage is lower than the close-range blade strike. */
    public void performWhipAttack() {
        if (!(level() instanceof ServerLevel server)) return;
        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }

        AABB reach = getBoundingBox().inflate(3.0D, 1.0D, 3.0D);
        for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class, reach,
                candidate -> candidate != this && HiveSwarmCoordinator.validTarget(this, candidate))) {
            Vec3 offset = target.position().subtract(position());
            Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
            if (offset.lengthSqr() > 9.0D || horizontal.lengthSqr() < 1.0E-8D
                    || forward.dot(horizontal.normalize()) < -0.15D || !hasLineOfSight(target)) continue;
            if (target.hurt(server.damageSources().mobAttack(this), 2.5F)) {
                target.knockback(0.3D, getX() - target.getX(), getZ() - target.getZ());
            }
        }
        server.sendParticles(ParticleTypes.SWEEP_ATTACK, getX() + forward.x, getY(0.5D),
                getZ() + forward.z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        server.playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_WHIP.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_SKELETON_BONECRACK.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        level().playSound(null, pos, ModSounds.FLESH_BLOCK_STEP.get(), SoundSource.HOSTILE, 0.15F, 1.0F);
    }

    /** One melee goal handles both close blade strikes and the mid-range whip. */
    private static final class InfectedSkeletonAttackGoal extends MeleeAttackGoal {
        private static final int WHIP_IMPACT_TICK = 4;
        private static final int WHIP_COOLDOWN_TICKS = 30;
        private final InfectedSkeletonEntity skeleton;
        private LivingEntity whipTarget;
        private int whipWindup;
        private int nextWhipTick;

        private InfectedSkeletonAttackGoal(InfectedSkeletonEntity skeleton, double speed) {
            super(skeleton, speed, false);
            this.skeleton = skeleton;
        }

        @Override
        protected void checkAndPerformAttack(LivingEntity target, double distanceToTargetSqr) {
            // A direct target assigned by HurtByTargetGoal may bypass target-selection predicates.
            // Do not clear it: movement/navigation may still bring a valid target into range.
            if (!skeleton.canAttackNow(target)) return;
            boolean inWhipBand = distanceToTargetSqr >= 2.25D && distanceToTargetSqr <= 9.0D;
            if (whipTarget != null) {
                if (target != whipTarget || !inWhipBand || !skeleton.canAttackNow(target)) {
                    whipTarget = null;
                    whipWindup = 0;
                } else if (--whipWindup <= 0) {
                    skeleton.performWhipAttack();
                    nextWhipTick = skeleton.tickCount + WHIP_COOLDOWN_TICKS;
                    whipTarget = null;
                }
                return;
            }
            if (inWhipBand) {
                if (skeleton.tickCount >= nextWhipTick && skeleton.canAttackNow(target)) {
                    whipTarget = target;
                    whipWindup = WHIP_IMPACT_TICK;
                    skeleton.beginWhipAnimation();
                }
                return;
            }
            if (distanceToTargetSqr < 2.25D) super.checkAndPerformAttack(target, distanceToTargetSqr);
        }
    }
}
```


## `src/main/java/com/carnis/mod/entity/ai/GoalPriorityUtil.java`

```java
package com.carnis.mod.entity.ai;

import java.util.HashSet;
import java.util.Set;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import net.minecraft.world.entity.ai.goal.WrappedGoal;

/** Assigns the first unused selector priority when goals are registered dynamically. */
public final class GoalPriorityUtil {
    private GoalPriorityUtil() { }

    public static int firstUnused(GoalSelector selector) {
        Set<Integer> used = new HashSet<>();
        for (WrappedGoal goal : selector.getAvailableGoals()) used.add(goal.getPriority());
        int priority = 0;
        while (used.contains(priority)) priority++;
        return priority;
    }
}
```


## `src/main/java/com/carnis/mod/event/CarnisEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.HiveEntity;
import com.carnis.mod.entity.BiomassValued;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

/** Мгновенная награда за убийство; питание остаётся отдельной механикой. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisEvents {
    private CarnisEvents() { }

    @SubscribeEvent(priority = EventPriority.HIGH, receiveCanceled = true)
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;

        Entity killer = event.getSource().getEntity();
        if (event.isCanceled() || victim instanceof Player || killer == null || killer == victim) return;

        if (victim instanceof BiomassValued hiveVictim
                && (victim instanceof HiveEntity || victim instanceof HiveSentinelEntity
                || victim instanceof CerebralNexusEntity)) {
            // Explicit Hive values are awarded only to player killers; no generic multipliers.
            if (killer instanceof ServerPlayer player) awardBiomass(player, hiveVictim.getBiomassValue());
            return;
        }

        ServerPlayer recipient = null;
        if (killer instanceof ServerPlayer player) {
            // PersistentData является источником истины; API учитывает также дробную долю.
            float infection = PlayerInfectionApi.getInfectionLevel(player);
            if (infection <= 0.0F) return;
            recipient = player;
        } else if (killer instanceof HivemindLinkedMob) {
            if (victim instanceof HivemindLinkedMob) {
                return;
            }
            if (killer instanceof TamableAnimal tame && tame.getOwnerUUID() != null) {
                UUID ownerId = tame.getOwnerUUID();
                recipient = level.getServer().getPlayerList().getPlayer(ownerId);
                if (recipient == null) {
                    // Известный владелец не в сети: не приписываем его награду дикому Улью.
                    CarnisMod.LOGGER.warn("Не удалось начислить биомассу: владелец {} не в сети", ownerId);
                    return;
                }
            }
        } else {
            return;
        }

        long multiplier = 1L;
        if (InfectionHandler.isInfected(victim)) multiplier *= 2L;
        if (victim instanceof AssimilatingMob) multiplier *= 3L;
        long total = basePoints(victim) * multiplier;

        if (recipient != null) {
            ServerPlayer player = recipient;
            awardBiomass(player, total);
        } else {
            CarnisWorldData data = CarnisWorldData.get(level);
            data.addBiomassPoints(total);
            ModMessages.sendToPlayersInLevel(level);
        }
    }

    private static void awardBiomass(ServerPlayer player, long amount) {
        if (amount <= 0L) return;
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            CarnisMod.LOGGER.warn("Не удалось начислить биомассу игроку {}: Capability отсутствует", player.getUUID());
            return;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
        });
    }

    private static long basePoints(LivingEntity victim) {
        if (victim instanceof InfectedCreeperEntity || victim instanceof InfectedSpiderEntity) return 5L;
        // Редкие проверяются раньше Animal/Monster: торговая лама и виз входят в эти группы.
        EntityType<?> type = victim.getType();
        if (type == EntityType.ALLAY || type == EntityType.VEX || type == EntityType.WARDEN
                || type == EntityType.ELDER_GUARDIAN || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM || type == EntityType.TRADER_LLAMA) return 25L;
        if (victim instanceof Animal) return 5L;
        if (victim instanceof Monster) return 15L;
        return 5L;
    }
}
```


## `src/main/java/com/carnis/mod/event/HypnosisEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.EnumSet;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HypnosisEvents {
    private static final String UNTIL = "carnis:trance_until", POOL = "carnis:trance_pool";
    private HypnosisEvents() { }
    public static void apply(Mob mob, ServerLevel level, BlockPos pool) {
        mob.getPersistentData().putLong(UNTIL, level.getGameTime() + 60);
        if (pool == null) mob.getPersistentData().remove(POOL); else mob.getPersistentData().putLong(POOL, pool.asLong());
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level)) return;
        if (mob.tickCount % 10 != 0) return;
        boolean active = mob.getPersistentData().getLong(UNTIL) > level.getGameTime();
        TranceGoal found = null;
        for (var wrapped : mob.goalSelector.getAvailableGoals())
            if (wrapped.getGoal() instanceof TranceGoal g) { found = g; break; }
        if (active && found == null) mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), new TranceGoal(mob));
        else if (!active && found != null) {
            mob.goalSelector.removeGoal(found);
            mob.getPersistentData().remove(UNTIL);
            mob.getPersistentData().remove(POOL);
        }
    }
    private static final class TranceGoal extends Goal {
        private final Mob mob;
        TranceGoal(Mob mob) { this.mob = mob; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        @Override public boolean canUse() { return mob.level() instanceof ServerLevel l && mob.getPersistentData().getLong(UNTIL) > l.getGameTime(); }
        @Override public boolean canContinueToUse() { return canUse(); }
        @Override public void start() { mob.getNavigation().stop(); }
        @Override public void stop() { mob.getNavigation().stop(); }
        @Override public void tick() {
            if (!(mob.level() instanceof ServerLevel level)) return;
            if (!mob.getPersistentData().contains(POOL)) { mob.getNavigation().stop(); return; }
            BlockPos pool = BlockPos.of(mob.getPersistentData().getLong(POOL));
            if (!level.hasChunkAt(pool) || !level.getBlockState(pool).is(ModBlocks.STOMACH_POOL.get())) {
                mob.getNavigation().stop(); return;
            }
            if (mob.tickCount % 10 == 0) mob.getNavigation().moveTo(pool.getX() + .5D, pool.getY(), pool.getZ() + .5D, 0.9D);
        }
        @Override public boolean requiresUpdateEveryTick() { return true; }
    }
}
```


## `src/main/java/com/carnis/mod/event/StomachPoolAttractEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.entity.ai.StomachPoolAttractGoal;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class StomachPoolAttractEvents {
    private StomachPoolAttractEvents() { }

    public static boolean isAllowedType(EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null) return false;

        // Third-party mobs: allow land/passive categories, but not foreign MONSTER bosses.
        if (!id.getNamespace().equals("minecraft")) {
            return type.getCategory() == MobCategory.CREATURE
                    || type.getCategory() == MobCategory.AMBIENT;
        }

        // Vanilla MISC-category hosts that should still be attracted.
        if (type == EntityType.VILLAGER
                || type == EntityType.WANDERING_TRADER
                || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM
                || type == EntityType.TRADER_LLAMA) {
            return true;
        }

        MobCategory category = type.getCategory();
        if (category == MobCategory.CREATURE || category == MobCategory.AMBIENT) return true;
        if (category == MobCategory.MONSTER) {
            return type != EntityType.ENDER_DRAGON
                    && type != EntityType.WITHER
                    && type != EntityType.ELDER_GUARDIAN
                    && type != EntityType.WARDEN;
        }
        return false;
    }

    @SubscribeEvent
    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel) || !(event.getEntity() instanceof Mob mob)
                || !isAllowedType(mob.getType()) || NeuralMossBlock.isHive(mob)) return;

        for (var wrapped : mob.goalSelector.getAvailableGoals()) {
            if (wrapped.getGoal() instanceof StomachPoolAttractGoal) return;
        }

        StomachPoolAttractGoal attraction = new StomachPoolAttractGoal(mob);
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction.createHoldGoal());
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction);
    }
}
```


## `build.gradle`

```groovy
plugins {
    id 'eclipse'
    id 'maven-publish'
    id 'net.minecraftforge.gradle'
}

version = project.mod_version
group = "com.carnis.mod"
archivesBaseName = "${mod_id}"

java.toolchain.languageVersion = JavaLanguageVersion.of(17)

minecraft {
    mappings channel: 'official', version: "${minecraft_version}"
    copyIdeResources = true

    runs {
        configureEach {
            workingDirectory project.file('run')
            property 'forge.logging.markers', 'REGISTRIES'
            property 'forge.logging.console.level', 'debug'
            mods {
                "${mod_id}" {
                    source sourceSets.main
                }
            }
        }

        client {
            property 'forge.enabledGameTestNamespaces', mod_id
        }

        server {
            property 'forge.enabledGameTestNamespaces', mod_id
            args '--nogui'
        }

        data {
            workingDirectory project.file('run')
            args '--mod', mod_id, '--all',
                 '--output', file('src/generated/resources/'),
                 '--existing', file('src/main/resources/')
        }
    }
}

sourceSets.main.resources {
    srcDir 'src/generated/resources'
}

repositories {
    mavenCentral()
    maven {
        name = 'GeckoLib'
        url = 'https://dl.cloudsmith.io/public/geckolib3/geckolib/maven/'
    }
}

dependencies {
    minecraft "net.minecraftforge:forge:${minecraft_version}-${forge_version}"
    implementation fg.deobf("software.bernie.geckolib:geckolib-forge-${minecraft_version}:${geckolib_version}")
}

tasks.named('processResources', ProcessResources).configure {
    var replaceProperties = [
            minecraft_version      : minecraft_version,
            minecraft_version_range: minecraft_version_range,
            forge_version          : forge_version,
            forge_version_range    : forge_version_range,
            loader_version_range   : loader_version_range,
            mod_id                 : mod_id,
            mod_name               : mod_name,
            mod_license            : mod_license,
            mod_version            : mod_version,
            mod_author             : mod_author,
            mod_description        : mod_description
    ]
    inputs.properties replaceProperties

    filesMatching(['META-INF/mods.toml', 'pack.mcmeta']) {
        expand replaceProperties + [project: project]
    }

    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

tasks.named('jar', Jar).configure {
    manifest {
        attributes([
                'Specification-Title'     : mod_id,
                'Specification-Vendor'    : mod_author,
                'Specification-Version'   : '1',
                'Implementation-Title'    : project.name,
                'Implementation-Version'  : project.jar.archiveVersion,
                'Implementation-Vendor'   : mod_author,
                'Implementation-Timestamp': new Date().format("yyyy-MM-dd'T'HH:mm:ssZ")
        ])
    }
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
    finalizedBy 'reobfJar'
}

tasks.withType(JavaCompile).configureEach {
    options.encoding = 'UTF-8'
}
```


## `gradle.properties`

```properties
# Gradle settings
org.gradle.jvmargs=-Xmx3G -Dfile.encoding=UTF-8
org.gradle.daemon=false
org.gradle.parallel=false
org.gradle.workers.max=2
org.gradle.caching=true
org.gradle.configuration-cache=false
org.gradle.warning.mode=all

# Project properties
mod_id=carnis
mod_name=Carnis: Adaptive Hivemind
mod_license=MIT
mod_version=3.4.5
mod_author=BlockBaster3K
mod_description=The Living Swarm Update: Hive evolution, four parasitic stages, organogenesis, the Flesh Amalgam, Neuro-Resonator armor, the Bio-Purifier and Codex Carnis.

# Versions
minecraft_version=1.20.1
minecraft_version_range=[1.20.1]
forge_version=47.4.28
forge_version_range=[47.1.0,)
loader_version_range=[47,)
geckolib_version=4.4.4
mapping_channel=official
mapping_version=1.20.1
```


## `src/main/resources/META-INF/mods.toml`

```toml
modLoader="javafml"
loaderVersion="[47,)"
license="MIT"

[[mods]]
modId="carnis"
version="${mod_version}"
displayName="Carnis: Adaptive Hivemind"
displayVersion="${mod_version}"
authors="BlockBaster3K"
description='''The Living Swarm Update. An adaptive organic Hive evolves through four stages of parasitism, spreading living tissue and developing macroscopic organs. Explore the Pulsing Heart and its network, confront the Flesh Amalgam, and survive the Swarm with Neuro-Resonator armor, the Bio-Purifier, the Pneumatic Inoculator and the Codex Carnis.'''

[[dependencies.carnis]]
modId="forge"
mandatory=true
versionRange="[47.1.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1]"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="geckolib"
mandatory=true
versionRange="[4.4.4,)"
ordering="AFTER"
side="BOTH"
```
