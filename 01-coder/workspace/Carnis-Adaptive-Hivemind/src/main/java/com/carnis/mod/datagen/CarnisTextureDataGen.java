package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.google.common.hash.Hashing;
import net.minecraft.data.CachedOutput;
import net.minecraft.data.DataProvider;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraftforge.common.data.ExistingFileHelper;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public final class CarnisTextureDataGen implements DataProvider {
    private static final int SIZE = 32;
    private static final ExistingFileHelper.ResourceType TEXTURE_TYPE =
            new ExistingFileHelper.ResourceType(PackType.CLIENT_RESOURCES, ".png", "textures");

    private final PackOutput.PathProvider blocks;
    private final PackOutput.PathProvider entities;
    private final PackOutput.PathProvider items;
    private final PackOutput.PathProvider armor;
    private final List<Texture> textures = new ArrayList<>();

    public CarnisTextureDataGen(PackOutput output, ExistingFileHelper existingFiles) {
        blocks = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/block");
        entities = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/entity");
        items = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/item");
        armor = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/armor");

        register(existingFiles, "block", "creeping_tendrils", Kind.TENDRILS, 0);

        register(existingFiles, "item", "viral_dart", Kind.VIRAL_DART, 0);
        register(existingFiles, "item", "purification_dart", Kind.PURIFICATION_DART, 0);
        register(existingFiles, "item", "purification_serum", Kind.SERUM, 0);
        register(existingFiles, "item", "neural_binding_matrix", Kind.MATRIX, 0);
        register(existingFiles, "item", "creeping_tendrils", Kind.TENDRILS, 0);
        register(existingFiles, "item", "pneumatic_inoculator", Kind.INOCULATOR_ICON, 0);
        register(existingFiles, "item", "flesh_amalgam_spawn_egg", Kind.EGG, 0);
        register(existingFiles, "item", "tainted_sludge_bucket", Kind.BUCKET, 0);

    }

    private void register(ExistingFileHelper files, String folder, String name, Kind kind, int variant) {
        textures.add(new Texture(folder, name, kind, variant));
        files.trackGenerated(new ResourceLocation(CarnisMod.MOD_ID, folder + "/" + name), TEXTURE_TYPE);
    }

    @Override
    public CompletableFuture<?> run(CachedOutput cache) {
        try {
            for (Texture texture : textures) {
                BufferedImage image = createTexture(texture.kind(), texture.variant());
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                if (!ImageIO.write(image, "png", bytes)) throw new IOException("PNG writer unavailable");
                byte[] encoded = bytes.toByteArray();
                PackOutput.PathProvider provider = switch (texture.folder()) {
                    case "block" -> blocks;
                    case "entity" -> entities;
                    case "item" -> items;
                    case "armor" -> armor;
                    default -> throw new IllegalStateException("Unknown texture folder: " + texture.folder());
                };
                Path destination = provider.file(new ResourceLocation(CarnisMod.MOD_ID, texture.name()), "png");
                cache.writeIfNeeded(destination, encoded, Hashing.sha256().hashBytes(encoded));
            }
            return CompletableFuture.completedFuture(null);
        } catch (IOException exception) {
            return CompletableFuture.failedFuture(exception);
        }
    }

    @Override
    public String getName() {
        return "Carnis item and tendril textures";
    }

    private static BufferedImage createTexture(Kind kind, int variant) {
        return switch (kind) {
            case VIRAL_DART -> dart(false);
            case PURIFICATION_DART -> dart(true);
            case SERUM -> serum();
            case MATRIX -> matrix();
            case TENDRILS -> tendrils();
            case GUN_ICON, GUN_GEO -> purifier();
            case INOCULATOR_ICON, INOCULATOR_GEO -> inoculator();
            case HELMET -> armorItem(0);
            case CHESTPLATE -> armorItem(1);
            case LEGGINGS -> armorItem(2);
            case BOOTS -> armorItem(3);
            case EGG -> spawnEgg();
            case BUCKET -> sludgeBucket();
            case ARMOR_SHEET -> armorSheet();

        };
    }

    private static BufferedImage canvas() {
        return new BufferedImage(SIZE, SIZE, BufferedImage.TYPE_INT_ARGB);
    }

    private static BufferedImage dart(boolean clean) {
        BufferedImage image = canvas();
        int outline = clean ? 0xFF25303A : 0xFF372314;
        int shadow = clean ? 0xFF536875 : 0xFF79501F;
        int metal = clean ? 0xFF91A9B1 : 0xFFC09239;
        int shine = clean ? 0xFFDCE9E8 : 0xFFF5D778;
        int glass = clean ? 0xFF30545C : 0xFF532E35;
        int fluid = clean ? 0xFF48D1CC : 0xFFB81135;
        int bright = clean ? 0xFFAAFFED : 0xFFFF5260;
        line(image, 5, 26, 22, 9, 4, outline);
        line(image, 5, 25, 21, 9, 3, shadow);
        line(image, 6, 24, 21, 9, 2, metal);
        line(image, 7, 23, 20, 10, 0, shine);
        line(image, 11, 19, 17, 13, 2, glass);
        line(image, 11, 19, 17, 13, 1, fluid);
        line(image, 12, 17, 16, 13, 0, bright);
        line(image, 21, 9, 24, 6, 1, outline);
        line(image, 24, 6, 29, 1, 0, 0xFFC8DADE);
        return image;
    }

    private static BufferedImage serum() {
        BufferedImage img = canvas();
        disc(img, 16, 18, 8, 0xFF30545C);
        disc(img, 16, 18, 6, 0xFF48D1CC);
        line(img, 14, 8, 18, 8, 2, 0xFF91A9B1);
        return img;
    }

    private static BufferedImage matrix() {
        BufferedImage image = canvas();
        disc(image, 16, 16, 13, 0xFF1B1018);
        disc(image, 16, 16, 10, 0xFF54202B);
        line(image, 8, 11, 14, 15, 0, 0xFF9F293D);
        line(image, 14, 15, 20, 21, 0, 0xFF8C2238);
        return image;
    }

    private static BufferedImage tendrils() {
        BufferedImage image = canvas();
        line(image, 16, 31, 16, 15, 3, 0xFF3C0A1A);
        line(image, 16, 20, 8, 10, 2, 0xFF862740);
        line(image, 16, 20, 24, 10, 2, 0xFF862740);
        return image;
    }

    private static BufferedImage purifier() {
        BufferedImage img = canvas();
        line(img, 6, 22, 24, 10, 4, 0xFF2A2D32);
        line(img, 12, 18, 26, 8, 2, 0xFFD49A38);
        line(img, 24, 10, 28, 7, 1, 0xFF48D1CC);
        return img;
    }

    private static BufferedImage inoculator() {
        BufferedImage img = canvas();
        line(img, 8, 24, 22, 10, 3, 0xFF536875);
        disc(img, 15, 17, 4, 0xFF48D1CC);
        line(img, 22, 10, 27, 5, 0, 0xFFE0E5E5);
        return img;
    }

    private static BufferedImage armorItem(int part) {
        BufferedImage img = canvas();
        int base = 0xFF1E242B;
        int glow = 0xFF48D1CC;
        switch (part) {
            case 0 -> { disc(img, 16, 16, 10, base); line(img, 10, 16, 22, 16, 2, glow); }
            case 1 -> { disc(img, 16, 16, 12, base); disc(img, 16, 14, 4, glow); }
            case 2 -> { line(img, 10, 8, 10, 26, 4, base); line(img, 22, 8, 22, 26, 4, base); }
            case 3 -> { disc(img, 10, 20, 5, base); disc(img, 22, 20, 5, base); }
        }
        return img;
    }

    private static BufferedImage spawnEgg() {
        BufferedImage img = canvas();
        disc(img, 16, 16, 11, 0xFF8A1C30);
        disc(img, 12, 12, 3, 0xFF48D1CC);
        disc(img, 20, 18, 2, 0xFF48D1CC);
        return img;
    }

    private static BufferedImage sludgeBucket() {
        BufferedImage img = canvas();
        disc(img, 16, 18, 9, 0xFF889098);
        disc(img, 16, 17, 6, 0xFF2A0A15);
        return img;
    }

    private static BufferedImage armorSheet() {
        BufferedImage img = new BufferedImage(64, 64, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 64; y++) for (int x = 0; x < 64; x++) {
            img.setRGB(x, y, ((x + y) & 8) == 0 ? 0xFF1E242B : 0xFF2B333D);
        }
        for (int x = 4; x <= 12; x++) img.setRGB(x, 10, 0xFF48D1CC);
        return img;
    }

    private static void disc(BufferedImage image, int cx, int cy, int radius, int color) {
        for (int y = -radius; y <= radius; y++) {
            for (int x = -radius; x <= radius; x++) {
                if (x * x + y * y <= radius * radius) pixel(image, cx + x, cy + y, color);
            }
        }
    }

    private static void line(BufferedImage image, int x0, int y0, int x1, int y1, int width, int color) {
        int dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
        int dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
        int error = dx + dy;
        while (true) {
            disc(image, x0, y0, width, color);
            if (x0 == x1 && y0 == y1) break;
            int twice = 2 * error;
            if (twice >= dy) { error += dy; x0 += sx; }
            if (twice <= dx) { error += dx; y0 += sy; }
        }
    }

    private static void pixel(BufferedImage image, int x, int y, int color) {
        if (x >= 0 && y >= 0 && x < image.getWidth() && y < image.getHeight()) image.setRGB(x, y, color);
    }

    private enum Kind {
        VIRAL_DART, PURIFICATION_DART, SERUM, MATRIX, TENDRILS, GUN_ICON, GUN_GEO,
        INOCULATOR_ICON, INOCULATOR_GEO, HELMET, CHESTPLATE, LEGGINGS, BOOTS, EGG, BUCKET, ARMOR_SHEET
    }

    private record Texture(String folder, String name, Kind kind, int variant) { }
}
