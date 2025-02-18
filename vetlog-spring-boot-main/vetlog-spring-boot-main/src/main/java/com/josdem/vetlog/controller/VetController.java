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

import com.josdem.vetlog.command.UsernameCommand;
import com.josdem.vetlog.enums.VaccinationStatus;
import com.josdem.vetlog.service.PetService;
import com.josdem.vetlog.service.UserService;
import com.josdem.vetlog.service.VaccinationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Slf4j
@Controller
@RequestMapping("/vet")
@RequiredArgsConstructor
public class VetController {

    private final UserService userService;
    private final PetService petService;
    private final VaccinationService vaccinationService;

    @Value("${gcpUrl}")
    private String gcpUrl;

    @Value("${imageBucket}")
    private String imageBucket;

    @Value("${defaultImage}")
    private String defaultImage;

    @GetMapping("/form")
    ModelAndView form() {
        log.info("Searching pets");
        var modelAndView = new ModelAndView("vet/form");
        modelAndView.addObject("usernameCommand", new UsernameCommand());
        return modelAndView;
    }

    @PostMapping("/search")
    ModelAndView search(@Valid UsernameCommand command) {
        log.info("Listing pets");
        var modelAndView = new ModelAndView("vet/list");
        var user = userService.getByUsername(command.getUsername());
        var pets = petService.getPetsByUser(user);
        pets.forEach(pet -> pet.setVaccines(vaccinationService.getVaccinesByStatus(pet, VaccinationStatus.PENDING)));
        modelAndView.addObject("pets", pets);
        modelAndView.addObject("gcpImageUrl", gcpUrl + imageBucket + "/");
        modelAndView.addObject("defaultImage", defaultImage);
        return modelAndView;
    }
}
