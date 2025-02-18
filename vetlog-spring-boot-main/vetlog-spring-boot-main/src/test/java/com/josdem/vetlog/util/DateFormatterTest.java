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

import java.time.LocalDateTime;
import java.util.Locale;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.i18n.LocaleContextHolder;

@Slf4j
@SpringBootTest
class DateFormatterTest {

    public static final String ES = "es";

    @Autowired
    private DateFormatter dateFormatter;

    private final Locale currentUserLocale = LocaleContextHolder.getLocale();

    @Test
    @DisplayName("Formatting a date")
    void shouldFormatADate() {
        var date = LocalDateTime.parse("2021-11-17T10:15:00");

        var formattedDate = dateFormatter.formatToDate(date, currentUserLocale);

        if (currentUserLocale.getLanguage().equals(ES)) {
            assertEquals("17/11/2021", formattedDate);
        } else {
            assertEquals("11/17/2021", formattedDate);
        }
    }

    @Test
    @DisplayName("Formatting old date")
    void shouldFormatOldDate() {
        var date = LocalDateTime.parse("1999-08-18T10:14:00");

        var formattedDate = dateFormatter.formatToDate(date, currentUserLocale);

        if (currentUserLocale.getLanguage().equals(ES)) {
            assertEquals("18/08/1999", formattedDate);
        } else {
            assertEquals("08/18/1999", formattedDate);
        }
    }

    @Test
    @DisplayName("Formatting date for ES locale")
    void shouldFormatDateForEs() {
        var locale = Locale.of(ES, "ES");
        var date = LocalDateTime.parse("1999-08-18T10:14:00");

        var formattedDate = dateFormatter.formatToDate(date, locale);

        assertEquals("18/08/1999", formattedDate);
    }
}
