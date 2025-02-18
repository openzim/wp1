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

import java.util.Locale;
import org.springframework.stereotype.Component;

@Component
public class VaccineFormatter {

    public String format(String name, Locale locale) {
        if (!locale.getLanguage().equals("es")) {
            return name;
        }
        return switch (name) {
            case "DA2PP" -> "Quintuple Canina";
            case "Deworming" -> "Desparasitación";
            case "Rabies" -> "Rabia";
            case "FVRCP" -> "Tripe Felina";
            default -> name;
        };
    }
}
