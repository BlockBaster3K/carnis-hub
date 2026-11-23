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
import java.util.List;
import java.util.concurrent.CompletableFuture;

public final class CountermeasureItemTextureProvider implements DataProvider {
    private static final int TEXTURE_SIZE = 16;

    private static final ExistingFileHelper.ResourceType TEXTURE_RESOURCE_TYPE =
            new ExistingFileHelper.ResourceType(
                    PackType.CLIENT_RESOURCES,
                    ".png",
                    "textures"
            );

    private static final List<String> TEXTURE_NAMES = List.of(
            "purification_serum",
            "neuro_resonator_helmet"
    );

    private final PackOutput.PathProvider texturePathProvider;

    public CountermeasureItemTextureProvider(
            PackOutput output,
            ExistingFileHelper existingFileHelper
    ) {
        texturePathProvider = output.createPathProvider(
                PackOutput.Target.RESOURCE_PACK,
                "textures/item"
        );

        for (String textureName : TEXTURE_NAMES) {
            existingFileHelper.trackGenerated(
                    new ResourceLocation(
                            CarnisMod.MOD_ID,
                            "item/" + textureName
                    ),
                    TEXTURE_RESOURCE_TYPE
            );
        }
    }

    @Override
    public CompletableFuture<?> run(CachedOutput cachedOutput) {
        try {
            for (String textureName : TEXTURE_NAMES) {
                BufferedImage image = createTexture(textureName);
                byte[] pngData = encodePng(image);
                Path destination = texturePathProvider.file(
                        new ResourceLocation(CarnisMod.MOD_ID, textureName),
                        "png"
                );

                cachedOutput.writeIfNeeded(
                        destination,
                        pngData,
                        Hashing.sha256().hashBytes(pngData)
                );
            }

            return CompletableFuture.completedFuture(null);
        } catch (IOException exception) {
            return CompletableFuture.failedFuture(exception);
        }
    }

    @Override
    public String getName() {
        return "Carnis procedural countermeasure item textures";
    }

    private static BufferedImage createTexture(String textureName) {
        return switch (textureName) {
            case "purification_serum" -> createPurificationSerum();
            case "bio_purifier" -> createBioPurifier();
            case "neuro_resonator_helmet" -> createNeuroResonatorHelmet();
            default -> throw new IllegalArgumentException(
                    "Unknown countermeasure texture: " + textureName
            );
        };
    }

    private static BufferedImage createPurificationSerum() {
        BufferedImage image = emptyTexture();
        int outline = argb(255, 37, 50, 68);
        int glass = argb(190, 174, 232, 235);
        int highlight = argb(225, 238, 255, 255);
        int serum = argb(245, 42, 211, 190);
        int serumDark = argb(255, 13, 125, 130);
        int cap = argb(255, 116, 82, 58);
        int capLight = argb(255, 178, 128, 78);

        fillRect(image, 6, 1, 4, 2, cap);
        fillRect(image, 7, 1, 2, 1, capLight);
        fillRect(image, 6, 3, 4, 2, outline);
        fillRect(image, 7, 3, 2, 2, glass);

        for (int y = 5; y <= 13; y++) {
            int left = y == 5 ? 5 : 4;
            int right = y == 5 ? 10 : 11;

            for (int x = left; x <= right; x++) {
                boolean border = x == left
                        || x == right
                        || y == 13;
                int pixel = border ? outline : glass;

                if (!border && y >= 8) {
                    pixel = y >= 12 ? serumDark : serum;
                }

                image.setRGB(x, y, pixel);
            }
        }

        setPixel(image, 5, 6, highlight);
        setPixel(image, 5, 7, highlight);
        setPixel(image, 6, 8, highlight);
        setPixel(image, 9, 9, argb(255, 178, 255, 238));
        setPixel(image, 10, 10, serumDark);
        return image;
    }

    private static BufferedImage createBioPurifier() {
        BufferedImage image = emptyTexture();
        int outline = argb(255, 32, 30, 37);
        int metal = argb(255, 91, 101, 111);
        int metalLight = argb(255, 157, 173, 177);
        int grip = argb(255, 70, 43, 53);
        int tank = argb(255, 27, 139, 145);
        int tankLight = argb(255, 79, 225, 198);
        int heat = argb(255, 244, 92, 30);
        int heatLight = argb(255, 255, 196, 58);

        fillRect(image, 3, 5, 9, 5, outline);
        fillRect(image, 4, 6, 7, 3, metal);
        fillRect(image, 5, 6, 5, 1, metalLight);
        fillRect(image, 11, 6, 4, 3, outline);
        fillRect(image, 12, 7, 3, 1, heat);
        setPixel(image, 15, 7, heatLight);

        fillRect(image, 2, 8, 4, 6, outline);
        fillRect(image, 3, 9, 2, 4, tank);
        setPixel(image, 3, 9, tankLight);
        setPixel(image, 3, 10, tankLight);

        fillRect(image, 7, 9, 4, 2, outline);
        fillRect(image, 8, 10, 3, 4, outline);
        fillRect(image, 9, 11, 2, 2, grip);
        setPixel(image, 4, 4, metalLight);
        setPixel(image, 5, 4, outline);
        return image;
    }

    private static BufferedImage createNeuroResonatorHelmet() {
        BufferedImage image = emptyTexture();
        int outline = argb(255, 35, 25, 52);
        int shell = argb(255, 91, 46, 125);
        int shellLight = argb(255, 163, 76, 177);
        int interior = argb(255, 25, 19, 42);
        int resonance = argb(255, 52, 224, 211);
        int resonanceLight = argb(255, 179, 255, 239);

        for (int y = 3; y <= 11; y++) {
            int inset = y == 3 ? 3 : y == 4 ? 2 : 1;
            int left = 2 + inset;
            int right = 13 - inset;

            for (int x = left; x <= right; x++) {
                boolean border = x == left
                        || x == right
                        || y == 3;
                image.setRGB(x, y, border ? outline : shell);
            }
        }

        fillRect(image, 3, 8, 10, 4, interior);
        fillRect(image, 2, 9, 2, 4, outline);
        fillRect(image, 12, 9, 2, 4, outline);
        fillRect(image, 4, 4, 3, 1, shellLight);

        for (int y = 5; y <= 10; y++) {
            setPixel(image, 8, y, resonance);
        }
        for (int x = 5; x <= 11; x++) {
            setPixel(image, x, 7, resonance);
        }

        setPixel(image, 5, 7, resonanceLight);
        setPixel(image, 8, 5, resonanceLight);
        setPixel(image, 11, 7, resonanceLight);
        setPixel(image, 6, 10, resonance);
        setPixel(image, 10, 10, resonance);
        return image;
    }

    private static BufferedImage emptyTexture() {
        return new BufferedImage(
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                BufferedImage.TYPE_INT_ARGB
        );
    }

    private static void fillRect(
            BufferedImage image,
            int x,
            int y,
            int width,
            int height,
            int color
    ) {
        for (int offsetY = 0; offsetY < height; offsetY++) {
            for (int offsetX = 0; offsetX < width; offsetX++) {
                setPixel(image, x + offsetX, y + offsetY, color);
            }
        }
    }

    private static void setPixel(
            BufferedImage image,
            int x,
            int y,
            int color
    ) {
        if (x >= 0 && x < TEXTURE_SIZE && y >= 0 && y < TEXTURE_SIZE) {
            image.setRGB(x, y, color);
        }
    }

    private static int argb(int alpha, int red, int green, int blue) {
        return (clamp(alpha) << 24)
                | (clamp(red) << 16)
                | (clamp(green) << 8)
                | clamp(blue);
    }

    private static int clamp(int value) {
        return Math.max(0, Math.min(255, value));
    }

    private static byte[] encodePng(BufferedImage image) throws IOException {
        try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (!ImageIO.write(image, "png", output)) {
                throw new IOException("No PNG ImageIO writer is available");
            }
            return output.toByteArray();
        }
    }
}
