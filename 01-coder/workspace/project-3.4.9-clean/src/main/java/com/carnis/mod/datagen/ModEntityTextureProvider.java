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
import java.util.SplittableRandom;
import java.util.concurrent.CompletableFuture;

public final class ModEntityTextureProvider implements DataProvider {
    private static final int TEXTURE_SIZE = 128;
    private static final long TEXTURE_SEED = 0xF1E5A6A1L;

    private static final ExistingFileHelper.ResourceType TEXTURE_RESOURCE_TYPE =
            new ExistingFileHelper.ResourceType(
                    PackType.CLIENT_RESOURCES,
                    ".png",
                    "textures"
            );

    private final PackOutput.PathProvider texturePathProvider;

    public ModEntityTextureProvider(
            PackOutput output,
            ExistingFileHelper existingFileHelper
    ) {
        texturePathProvider = output.createPathProvider(
                PackOutput.Target.RESOURCE_PACK,
                "textures/entity"
        );

        trackTexture(existingFileHelper, "flesh_amalgam");
        trackTexture(existingFileHelper, "flesh_amalgam_glowmask");
    }

    private static void trackTexture(
            ExistingFileHelper existingFileHelper,
            String name
    ) {
        existingFileHelper.trackGenerated(
                new ResourceLocation(
                        CarnisMod.MOD_ID,
                        "entity/" + name
                ),
                TEXTURE_RESOURCE_TYPE
        );
    }

    @Override
    public CompletableFuture<?> run(CachedOutput cachedOutput) {
        try {
            writeTexture(
                    cachedOutput,
                    "flesh_amalgam",
                    createFleshAmalgamTexture(TEXTURE_SEED)
            );
            writeTexture(
                    cachedOutput,
                    "flesh_amalgam_glowmask",
                    createFleshAmalgamGlowmask(TEXTURE_SEED)
            );

            return CompletableFuture.completedFuture(null);
        } catch (IOException exception) {
            return CompletableFuture.failedFuture(exception);
        }
    }

    private void writeTexture(
            CachedOutput cachedOutput,
            String name,
            BufferedImage image
    ) throws IOException {
        byte[] pngData = encodePng(image);
        Path destination = texturePathProvider.file(
                new ResourceLocation(CarnisMod.MOD_ID, name),
                "png"
        );

        cachedOutput.writeIfNeeded(
                destination,
                pngData,
                Hashing.sha256().hashBytes(pngData)
        );
    }

    @Override
    public String getName() {
        return "Carnis procedural entity textures";
    }

    private static BufferedImage createFleshAmalgamTexture(long seed) {
        BufferedImage image = new BufferedImage(
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                BufferedImage.TYPE_INT_ARGB
        );
        SplittableRandom random = new SplittableRandom(seed);

        int darkFlesh = argb(75, 18, 34);
        int flesh = argb(132, 38, 57);
        int rawFlesh = argb(187, 66, 76);
        int vein = argb(91, 10, 31);
        int hotVein = argb(235, 57, 78);
        int bone = argb(190, 169, 131);
        int ichor = argb(218, 148, 52);

        for (int y = 0; y < TEXTURE_SIZE; y++) {
            for (int x = 0; x < TEXTURE_SIZE; x++) {
                int pixel = shade(
                        ((x / 16 + y / 16) & 1) == 0 ? flesh : darkFlesh,
                        random.nextInt(-14, 15)
                );

                if (isPrimaryVein(x, y)) {
                    pixel = mix(
                            vein,
                            hotVein,
                            0.25D + random.nextDouble() * 0.45D
                    );
                } else if (isCapillary(x, y, seed)) {
                    pixel = mix(pixel, vein, 0.66D);
                } else if (isBonePlate(x, y)) {
                    pixel = mix(
                            bone,
                            rawFlesh,
                            random.nextDouble(0.08D, 0.30D)
                    );
                } else if (random.nextDouble() < 0.055D) {
                    pixel = mix(pixel, rawFlesh, 0.48D);
                }

                if (isIchorNodule(x, y, seed)) {
                    pixel = mix(pixel, ichor, 0.84D);
                }

                image.setRGB(x, y, pixel);
            }
        }

        paintBaseEye(image, 78, 107, 4, 2);
        paintBaseEye(image, 70, 15, 4, 2);
        paintBaseEye(image, 88, 14, 3, 2);

        return image;
    }

    private static BufferedImage createFleshAmalgamGlowmask(long seed) {
        BufferedImage image = new BufferedImage(
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                BufferedImage.TYPE_INT_ARGB
        );

        int veinGlow = argb(184, 255, 42, 64);
        int noduleGlow = argb(235, 255, 176, 69);

        for (int y = 0; y < TEXTURE_SIZE; y++) {
            for (int x = 0; x < TEXTURE_SIZE; x++) {
                if (isIchorNodule(x, y, seed)) {
                    image.setRGB(x, y, noduleGlow);
                } else if (isPrimaryVein(x, y) && (x + y) % 3 != 0) {
                    image.setRGB(x, y, veinGlow);
                } else {
                    image.setRGB(x, y, 0x00000000);
                }
            }
        }

        paintGlowEye(image, 78, 107, 4, 2);
        paintGlowEye(image, 70, 15, 4, 2);
        paintGlowEye(image, 88, 14, 3, 2);

        return image;
    }

    private static void paintBaseEye(
            BufferedImage image,
            int centerX,
            int centerY,
            int radiusX,
            int radiusY
    ) {
        for (int y = centerY - radiusY - 1; y <= centerY + radiusY + 1; y++) {
            for (int x = centerX - radiusX - 1; x <= centerX + radiusX + 1; x++) {
                double normalizedDistance = square(
                        (x - centerX) / (double) radiusX
                ) + square((y - centerY) / (double) radiusY);

                if (
                        normalizedDistance > 1.0D
                                || x < 0
                                || y < 0
                                || x >= TEXTURE_SIZE
                                || y >= TEXTURE_SIZE
                ) {
                    continue;
                }

                int pixel = Math.abs(x - centerX) <= Math.max(1, radiusX / 3)
                        ? argb(27, 8, 18)
                        : argb(218, 157, 50);

                if (x == centerX - 1 && y == centerY - 1) {
                    pixel = argb(255, 238, 211);
                }

                image.setRGB(x, y, pixel);
            }
        }
    }

    private static void paintGlowEye(
            BufferedImage image,
            int centerX,
            int centerY,
            int radiusX,
            int radiusY
    ) {
        for (int y = centerY - radiusY - 1; y <= centerY + radiusY + 1; y++) {
            for (int x = centerX - radiusX - 1; x <= centerX + radiusX + 1; x++) {
                double normalizedDistance = square(
                        (x - centerX) / (double) radiusX
                ) + square((y - centerY) / (double) radiusY);

                if (
                        normalizedDistance > 1.0D
                                || x < 0
                                || y < 0
                                || x >= TEXTURE_SIZE
                                || y >= TEXTURE_SIZE
                ) {
                    continue;
                }

                if (Math.abs(x - centerX) <= Math.max(1, radiusX / 3)) {
                    image.setRGB(x, y, 0x00000000);
                } else {
                    image.setRGB(x, y, argb(230, 255, 154, 43));
                }
            }
        }
    }

    private static double square(double value) {
        return value * value;
    }

    private static boolean isPrimaryVein(int x, int y) {
        double firstCenter = 26.0D
                + Math.sin(y * 0.13D) * 11.0D
                + Math.sin(y * 0.037D) * 7.0D;
        double secondCenter = 94.0D
                + Math.sin(y * 0.095D + 1.7D) * 14.0D;

        return Math.abs(x - firstCenter) < 1.25D
                || Math.abs(x - secondCenter) < 1.05D;
    }

    private static boolean isCapillary(int x, int y, long seed) {
        long hash = coordinateHash(x, y, seed);
        boolean branchBand = Math.abs(
                y - (x * 0.48D + 18.0D + Math.sin(x * 0.18D) * 9.0D)
        ) < 0.85D;

        return branchBand || Math.floorMod(hash, 89L) == 0L;
    }

    private static boolean isBonePlate(int x, int y) {
        int localX = x & 31;
        int localY = y & 31;
        double deltaX = localX - 23.0D;
        double deltaY = localY - 8.0D;

        return deltaX * deltaX / 44.0D + deltaY * deltaY / 18.0D < 1.0D
                && (x / 32 + y / 32) % 3 == 0;
    }

    private static boolean isIchorNodule(int x, int y, long seed) {
        long hash = coordinateHash(x / 3, y / 3, seed ^ 0x1C4012L);

        return Math.floorMod(hash, 151L) == 0L
                && ((x + y) & 1) == 0;
    }

    private static long coordinateHash(int x, int y, long seed) {
        long value = seed;
        value ^= (long) x * 0x9E3779B97F4A7C15L;
        value ^= (long) y * 0xC2B2AE3D27D4EB4FL;
        value ^= value >>> 29;
        value *= 0x165667B19E3779F9L;

        return value ^ (value >>> 32);
    }

    private static byte[] encodePng(BufferedImage image) throws IOException {
        try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (!ImageIO.write(image, "png", output)) {
                throw new IOException("No PNG ImageIO writer is available");
            }
            return output.toByteArray();
        }
    }

    private static int argb(int red, int green, int blue) {
        return argb(255, red, green, blue);
    }

    private static int argb(int alpha, int red, int green, int blue) {
        return (clamp(alpha) << 24)
                | (clamp(red) << 16)
                | (clamp(green) << 8)
                | clamp(blue);
    }

    private static int shade(int color, int amount) {
        return argb(
                ((color >> 16) & 0xFF) + amount,
                ((color >> 8) & 0xFF) + amount,
                (color & 0xFF) + amount
        );
    }

    private static int mix(int first, int second, double ratio) {
        double clampedRatio = Math.max(0.0D, Math.min(1.0D, ratio));
        double inverse = 1.0D - clampedRatio;

        int red = (int) Math.round(
                ((first >> 16) & 0xFF) * inverse
                        + ((second >> 16) & 0xFF) * clampedRatio
        );
        int green = (int) Math.round(
                ((first >> 8) & 0xFF) * inverse
                        + ((second >> 8) & 0xFF) * clampedRatio
        );
        int blue = (int) Math.round(
                (first & 0xFF) * inverse
                        + (second & 0xFF) * clampedRatio
        );

        return argb(red, green, blue);
    }

    private static int clamp(int value) {
        return Math.max(0, Math.min(255, value));
    }
}
