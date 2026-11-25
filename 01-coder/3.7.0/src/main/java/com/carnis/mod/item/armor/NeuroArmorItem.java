package com.carnis.mod.item.armor;

import com.carnis.mod.client.renderer.NeuroArmorRenderer;
import com.carnis.mod.init.ModArmorMaterials;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.function.Consumer;

public class NeuroArmorItem extends ArmorItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public NeuroArmorItem(Type type, Properties properties) {
        super(ModArmorMaterials.NEURO_RESONATOR, type, properties);
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) { }
    @Override public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private NeuroArmorRenderer renderer;
            @Override public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity, ItemStack stack,
                    EquipmentSlot slot, HumanoidModel<?> original) {
                if (renderer == null) renderer = new NeuroArmorRenderer();
                renderer.prepForRender(entity, stack, slot, original);
                return renderer;
            }
        });
    }
}
