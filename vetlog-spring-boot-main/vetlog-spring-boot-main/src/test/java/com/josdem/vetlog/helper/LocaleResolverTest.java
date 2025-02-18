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

package com.josdem.vetlog.helper;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Locale;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@Slf4j
class LocaleResolverTest {

    private final LocaleResolver localeResolver = new LocaleResolver();
    private final HttpServletRequest request = mock(HttpServletRequest.class);

    @Test
    @DisplayName("getting default locale")
    void shouldGetDefaultLocale(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var result = localeResolver.resolveLocale(request);
        assertEquals(Locale.of("en"), result);
    }

    @DisplayName("getting english from headers")
    @ParameterizedTest
    @ValueSource(strings = {"en-US,en;q=0.8", "zh-cn,zh-tw"})
    void shouldGetLocaleFromHeaders(String headers) {
        log.info("Running: getting english from headers");
        when(request.getHeader("Accept-Language")).thenReturn(headers);
        var result = localeResolver.resolveLocale(request);
        assertEquals(Locale.of("en"), result);
    }

    @Test
    @DisplayName("getting spanish from headers")
    void shouldGetSpanishFromHeaders(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        when(request.getHeader("Accept-Language")).thenReturn("es-MX,en-US;q=0.7,en;q=0.3");
        var result = localeResolver.resolveLocale(request);
        assertEquals(Locale.of("es"), result);
    }
}
