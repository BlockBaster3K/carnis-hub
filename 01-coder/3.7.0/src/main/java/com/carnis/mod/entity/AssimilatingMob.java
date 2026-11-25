package com.carnis.mod.entity;

/** Network-synchronised visual state and final biomass value for assimilating mobs. */
public interface AssimilatingMob extends BiomassValued {
    boolean isAssimilating();
    void setAssimilating(boolean assimilating);
}
