/*
  Copyright 2025 Jose Morales contact@josdem.io

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

package com.josdem.vetlog.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Locale;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

@Slf4j
class VaccineFormatterTest {

    @InjectMocks
    private final VaccineFormatter vaccineFormatter = new VaccineFormatter();

    @Mock
    private Locale locale;

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    @DisplayName("formatting DA2PP if locale is Spanish")
    void shouldFormatDA2PPInSpanish(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        when(locale.getLanguage()).thenReturn("es");

        assertEquals("Quintuple Canina", vaccineFormatter.format("DA2PP", locale));
    }

    @Test
    @DisplayName("formatting deworming if locale is Spanish")
    void shouldFormatDewormingInSpanish(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        when(locale.getLanguage()).thenReturn("es");

        assertEquals("Desparasitación", vaccineFormatter.format("Deworming", locale));
    }

    @Test
    @DisplayName("formatting rabies if locale is Spanish")
    void shouldFormatRabiesInSpanish(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        when(locale.getLanguage()).thenReturn("es");

        assertEquals("Rabia", vaccineFormatter.format("Rabies", locale));
    }

    @Test
    @DisplayName("formatting FVRCP if locale is Spanish")
    void shouldFormatFVRCPInSpanish(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        when(locale.getLanguage()).thenReturn("es");

        assertEquals("Tripe Felina", vaccineFormatter.format("FVRCP", locale));
    }

    @Test
    @DisplayName("not formatting DA2PP if locale is Sengish")
    void shouldNotFormatDA2PP(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        when(locale.getLanguage()).thenReturn("en");

        assertEquals("DA2PP", vaccineFormatter.format("DA2PP", locale));
    }
}
