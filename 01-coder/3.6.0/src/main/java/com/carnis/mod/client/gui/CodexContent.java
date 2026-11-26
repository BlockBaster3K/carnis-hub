package com.carnis.mod.client.gui;

import java.util.List;

/** Field notes use translation keys; each entry is paginated by the active game font. */
public final class CodexContent {
    public record Page(String title, String body, String note) { }
    public record Chapter(String title, List<Page> pages) { }

    public static final List<Chapter> CHAPTERS = List.of(
        new Chapter("codex.carnis.tab.0", List.of(
            new Page("codex.carnis.entry.0.title", "codex.carnis.entry.0.body", "codex.carnis.entry.0.note"),
            new Page("codex.carnis.entry.1.title", "codex.carnis.entry.1.body", "codex.carnis.entry.1.note"),
            new Page("codex.carnis.entry.2.title", "codex.carnis.entry.2.body", "codex.carnis.entry.2.note"),
            new Page("codex.carnis.entry.3.title", "codex.carnis.entry.3.body", "codex.carnis.entry.3.note"),
            new Page("codex.carnis.entry.4.title", "codex.carnis.entry.4.body", "codex.carnis.entry.4.note"),
            new Page("codex.carnis.entry.5.title", "codex.carnis.entry.5.body", "codex.carnis.entry.5.note"))),
        new Chapter("codex.carnis.tab.1", List.of(
            new Page("codex.carnis.entry.6.title", "codex.carnis.entry.6.body", "codex.carnis.entry.6.note"),
            new Page("codex.carnis.entry.7.title", "codex.carnis.entry.7.body", "codex.carnis.entry.7.note"),
            new Page("codex.carnis.entry.8.title", "codex.carnis.entry.8.body", "codex.carnis.entry.8.note"),
            new Page("codex.carnis.entry.9.title", "codex.carnis.entry.9.body", "codex.carnis.entry.9.note"),
            new Page("codex.carnis.entry.10.title", "codex.carnis.entry.10.body", "codex.carnis.entry.10.note"))),
        new Chapter("codex.carnis.tab.2", List.of(
            new Page("codex.carnis.entry.11.title", "codex.carnis.entry.11.body", "codex.carnis.entry.11.note"),
            new Page("codex.carnis.entry.12.title", "codex.carnis.entry.12.body", "codex.carnis.entry.12.note"),
            new Page("codex.carnis.entry.13.title", "codex.carnis.entry.13.body", "codex.carnis.entry.13.note"),
            new Page("codex.carnis.entry.14.title", "codex.carnis.entry.14.body", "codex.carnis.entry.14.note"))),
        new Chapter("codex.carnis.tab.3", List.of(
            new Page("codex.carnis.entry.15.title", "codex.carnis.entry.15.body", "codex.carnis.entry.15.note"),
            new Page("codex.carnis.entry.16.title", "codex.carnis.entry.16.body", "codex.carnis.entry.16.note"),
            new Page("codex.carnis.entry.17.title", "codex.carnis.entry.17.body", "codex.carnis.entry.17.note"),
            new Page("codex.carnis.entry.18.title", "codex.carnis.entry.18.body", "codex.carnis.entry.18.note"),
            new Page("codex.carnis.entry.19.title", "codex.carnis.entry.19.body", "codex.carnis.entry.19.note")))
    );
    private CodexContent() { }
}
