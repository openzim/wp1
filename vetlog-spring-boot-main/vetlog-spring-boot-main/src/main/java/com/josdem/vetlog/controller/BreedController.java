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

package com.josdem.vetlog.controller;

import com.josdem.vetlog.enums.PetType;
import com.josdem.vetlog.model.Breed;
import com.josdem.vetlog.service.BreedService;
import jakarta.servlet.http.HttpServletResponse;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/breed")
@RequiredArgsConstructor
public class BreedController {

    public static final String DOMAIN = "vetlog.org";
    private final BreedService breedService;

    @GetMapping(value = "/list")
    public List<Breed> listByType(@RequestParam String type, HttpServletResponse response) {
        log.info("Listing Pets by type: {}", type);

        response.addHeader("Allow-Control-Allow-Methods", "GET");
        response.addHeader("Access-Control-Allow-Origin", DOMAIN);
        return breedService.getBreedsByType(PetType.getPetTypeByValue(type));
    }
}
