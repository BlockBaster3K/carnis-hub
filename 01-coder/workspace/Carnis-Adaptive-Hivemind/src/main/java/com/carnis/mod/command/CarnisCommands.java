package com.carnis.mod.command;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.LongArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.DynamicCommandExceptionType;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Locale;
import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class CarnisCommands {
    private static final int REQUIRED_PERMISSION_LEVEL = 2;
    private static final int DEFAULT_SHOCK_RADIUS_CHUNKS =
            CarnisWorldData.SYNAPSE_SHOCK_RADIUS_CHUNKS;
    private static final int MAX_SHOCK_RADIUS_CHUNKS = 16;

    private static final String VALID_ADAPTATION_TYPES =
            "FIRE, RANGED, MELEE, PILLARING, EXPLOSIVE, DARK";

    private static final DynamicCommandExceptionType
            INVALID_ADAPTATION_TYPE = new DynamicCommandExceptionType(
                    value -> Component.literal(
                            "Неизвестный тип адаптации '"
                                    + value
                                    + "'. Допустимые значения: "
                                    + VALID_ADAPTATION_TYPES
                    )
            );

    private CarnisCommands() {
    }

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        register(event.getDispatcher());
    }

    private static void register(
            CommandDispatcher<CommandSourceStack> dispatcher
    ) {
        dispatcher.register(
                Commands.literal("carnis")
                        .requires(
                                source -> source.hasPermission(
                                        REQUIRED_PERMISSION_LEVEL
                                )
                        )
                        .then(
                                Commands.literal("infection")
                                        .then(Commands.argument("targets", EntityArgument.players())
                                                .then(Commands.literal("get")
                                                        .executes(context -> infection(context, "get")))
                                                .then(Commands.literal("set")
                                                        .then(Commands.argument("value", FloatArgumentType.floatArg(0.0F, 100.0F))
                                                                .executes(context -> infection(context, "set"))))
                                                .then(Commands.literal("add")
                                                        .then(Commands.argument("value", FloatArgumentType.floatArg())
                                                                .executes(context -> infection(context, "add")))))
                        )
                        .then(
                                Commands.literal("info")
                                        .executes(CarnisCommands::showInfo)
                        )
                        .then(
                                Commands.literal("add_points")
                                        .then(
                                                Commands.argument(
                                                                "amount",
                                                                LongArgumentType.longArg(1L, 1000000L)
                                                        )
                                                        .executes(
                                                                CarnisCommands::addPoints
                                                        )
                                        )
                        )
                        .then(
                                Commands.literal("set_points")
                                        .then(
                                                Commands.argument(
                                                                "amount",
                                                                LongArgumentType.longArg(0L, 1000000L)
                                                        )
                                                        .executes(CarnisCommands::setPoints)
                                        )
                        )
                        .then(
                                Commands.literal("set_adaptation")
                                        .then(
                                                Commands.argument(
                                                                "type",
                                                                StringArgumentType.word()
                                                        )
                                                        .suggests(
                                                                CarnisCommands::suggestAdaptationTypes
                                                        )
                                                        .then(
                                                                Commands.argument(
                                                                                "level",
                                                                                LongArgumentType.longArg(
                                                                                        0L
                                                                                )
                                                                        )
                                                                        .executes(
                                                                                CarnisCommands::setAdaptation
                                                                        )
                                                        )
                                        )
                        )
                        .then(
                                Commands.literal("shock_chunk")
                                        .executes(
                                                context -> shockChunk(
                                                        context,
                                                        DEFAULT_SHOCK_RADIUS_CHUNKS
                                                )
                                        )
                                        .then(
                                                Commands.argument(
                                                                "radius",
                                                                IntegerArgumentType.integer(
                                                                        0,
                                                                        MAX_SHOCK_RADIUS_CHUNKS
                                                                )
                                                        )
                                                        .executes(
                                                                context -> shockChunk(
                                                                        context,
                                                                        IntegerArgumentType.getInteger(
                                                                                context,
                                                                                "radius"
                                                                        )
                                                                )
                                                        )
                                        )
                        )
        );
    }

    private static int infection(CommandContext<CommandSourceStack> context, String action)
            throws CommandSyntaxException {
        var players = EntityArgument.getPlayers(context, "targets");
        float amount = action.equals("get") ? 0.0F : FloatArgumentType.getFloat(context, "value");
        for (ServerPlayer player : players) {
            if (action.equals("set")) {
                PlayerInfectionApi.setInfectionLevel(player, amount);
            } else if (action.equals("add")) {
                PlayerInfectionApi.addInfection(player, amount);
            }
            float current = PlayerInfectionApi.getInfectionLevel(player);
            context.getSource().sendSuccess(
                    () -> Component.literal(player.getGameProfile().getName() + ": " + current + "%"),
                    !action.equals("get")
            );
        }
        return players.size();
    }

    private static int showInfo(
            CommandContext<CommandSourceStack> context
    ) {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        ChunkPos chunkPos = getSourceChunk(source);
        long currentGameTime = serverLevel.getGameTime();
        Long expiresAt = worldData.getShockedChunks().get(chunkPos);
        long remainingShockTicks = expiresAt == null
                || expiresAt <= currentGameTime
                ? 0L
                : expiresAt - currentGameTime;
        long remainingShockSeconds = remainingShockTicks / 20L;

        if (remainingShockTicks % 20L != 0L) {
            remainingShockSeconds++;
        }

        source.sendSuccess(
                () -> Component.literal(
                                "=== Carnis: Adaptive Hivemind ==="
                        )
                        .withStyle(ChatFormatting.DARK_RED),
                false
        );
        source.sendSuccess(
                () -> Component.literal(
                        "Измерение: "
                                + serverLevel.dimension().location()
                ),
                false
        );
        source.sendSuccess(
                () -> Component.literal(
                                "Очки биомассы: "
                                        + worldData.getBiomassPoints()
                        )
                        .withStyle(ChatFormatting.GOLD),
                false
        );

        if (remainingShockTicks > 0L) {
            long displayedSeconds = remainingShockSeconds;
            source.sendSuccess(
                    () -> Component.literal(
                                    "Чанк ["
                                            + chunkPos.x
                                            + ", "
                                            + chunkPos.z
                                            + "]: ШОК АКТИВЕН, осталось "
                                            + displayedSeconds
                                            + " с ("
                                            + remainingShockTicks
                                            + " тиков)"
                            )
                            .withStyle(ChatFormatting.AQUA),
                    false
            );
        } else {
            source.sendSuccess(
                    () -> Component.literal(
                                    "Чанк ["
                                            + chunkPos.x
                                            + ", "
                                            + chunkPos.z
                                            + "]: шок неактивен"
                            )
                            .withStyle(ChatFormatting.GRAY),
                    false
            );
        }

        source.sendSuccess(
                () -> Component.literal("Матрица адаптации:")
                        .withStyle(ChatFormatting.DARK_AQUA),
                false
        );

        for (AdaptationType type : AdaptationType.values()) {
            long adaptationLevel = worldData.getAdaptation(type);
            source.sendSuccess(
                    () -> Component.literal(
                            "  " + type.name() + ": " + adaptationLevel
                    ),
                    false
            );
        }

        return 1;
    }

    private static int addPoints(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        long amount = LongArgumentType.getLong(context, "amount");
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            player.sendSystemMessage(Component.literal(
                    "§c[Carnis] Ошибка: данные биомассы не найдены"));
            return 0;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
            player.sendSystemMessage(Component.literal(
                    "§a[Carnis] Добавлено " + amount + " биомассы. Итого: "
                            + data.getBiomassPoints()));
        });
        return 1;
    }

    private static int setPoints(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        long amount = LongArgumentType.getLong(context, "amount");
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            player.sendSystemMessage(Component.literal(
                    "§c[Carnis] Ошибка: данные биомассы не найдены"));
            return 0;
        }
        biomass.ifPresent(data -> {
            data.setBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
            player.sendSystemMessage(Component.literal(
                    "§a[Carnis] Биомасса установлена: " + amount));
        });
        return amount > 0L ? 1 : 0;
    }

    private static int setAdaptation(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        String rawType = StringArgumentType.getString(context, "type");
        AdaptationType type = parseAdaptationType(rawType);
        long requestedLevel = LongArgumentType.getLong(context, "level");
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        long previousLevel = worldData.getAdaptation(type);
        long updatedLevel = worldData.setAdaptation(type, requestedLevel);
        boolean changed = updatedLevel != previousLevel;

        if (changed) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        ChatFormatting color = changed
                ? ChatFormatting.GREEN
                : ChatFormatting.YELLOW;
        source.sendSuccess(
                () -> Component.literal(
                                "Адаптация "
                                        + type.name()
                                        + ": "
                                        + previousLevel
                                        + " -> "
                                        + updatedLevel
                        )
                        .withStyle(color),
                changed
        );

        return 1;
    }

    private static int shockChunk(
            CommandContext<CommandSourceStack> context,
            int radiusChunks
    ) {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        ChunkPos centerChunk = getSourceChunk(source);
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        int changedChunks = worldData.shockChunkArea(
                centerChunk,
                radiusChunks,
                serverLevel.getGameTime()
        );
        boolean changed = changedChunks > 0;

        if (changed) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        int diameterChunks = radiusChunks * 2 + 1;
        long durationSeconds =
                CarnisWorldData.SYNAPSE_SHOCK_DURATION_TICKS / 20L;
        ChatFormatting color = changed
                ? ChatFormatting.AQUA
                : ChatFormatting.YELLOW;

        source.sendSuccess(
                () -> Component.literal(
                                "Шок чанков: центр ["
                                        + centerChunk.x
                                        + ", "
                                        + centerChunk.z
                                        + "], радиус "
                                        + radiusChunks
                                        + ", область "
                                        + diameterChunks
                                        + "x"
                                        + diameterChunks
                                        + ", длительность "
                                        + durationSeconds
                                        + " с, обновлено чанков: "
                                        + changedChunks
                        )
                        .withStyle(color),
                changed
        );

        return 1;
    }

    private static AdaptationType parseAdaptationType(String rawType)
            throws CommandSyntaxException {
        try {
            return AdaptationType.valueOf(
                    rawType.toUpperCase(Locale.ROOT)
            );
        } catch (IllegalArgumentException exception) {
            throw INVALID_ADAPTATION_TYPE.create(rawType);
        }
    }

    private static CompletableFuture<Suggestions> suggestAdaptationTypes(
            CommandContext<CommandSourceStack> context,
            SuggestionsBuilder builder
    ) {
        String remaining = builder.getRemaining().toUpperCase(Locale.ROOT);

        for (AdaptationType type : AdaptationType.values()) {
            if (type.name().startsWith(remaining)) {
                builder.suggest(type.name());
            }
        }

        return builder.buildFuture();
    }

    private static ChunkPos getSourceChunk(CommandSourceStack source) {
        return new ChunkPos(BlockPos.containing(source.getPosition()));
    }
}
