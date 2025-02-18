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

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Locale;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.i18n.AcceptHeaderLocaleResolver;

@Slf4j
@Component
@RequiredArgsConstructor
public class LocaleResolver extends AcceptHeaderLocaleResolver {

    private static final Locale ENGLISH = Locale.of("en");
    private static final Locale SPANISH = Locale.of("es");
    private static final List<Locale> LOCALES = List.of(ENGLISH, SPANISH);

    public static final String ACCEPT_LANGUAGE = "Accept-Language";

    @NotNull
    @Override
    public Locale resolveLocale(HttpServletRequest request) {
        log.info("Accept Language: {}", request.getHeader(ACCEPT_LANGUAGE));
        if (request.getHeader(ACCEPT_LANGUAGE) == null) {
            return ENGLISH;
        }
        List<Locale.LanguageRange> list = Locale.LanguageRange.parse(request.getHeader(ACCEPT_LANGUAGE));
        Locale locale = Locale.lookup(list, LOCALES);
        return locale != null ? locale : ENGLISH;
    }
}
