package com.carnis.mod.fluid;

import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
import net.minecraftforge.fluids.FluidType;
import java.util.function.Consumer;

public final class TaintedSludgeType extends FluidType {
    public TaintedSludgeType() {
        super(FluidType.Properties.create().density(1600).viscosity(2400));
    }

    @Override
    public void initializeClient(Consumer<IClientFluidTypeExtensions> consumer) {
        consumer.accept(new IClientFluidTypeExtensions() {
            @Override public ResourceLocation getStillTexture() { return new ResourceLocation("carnis", "block/tainted_sludge_still"); }
            @Override public ResourceLocation getFlowingTexture() { return new ResourceLocation("carnis", "block/tainted_sludge_flow"); }
            @Override public int getTintColor() { return 0xFF8A1A22; }
        });
    }
}
