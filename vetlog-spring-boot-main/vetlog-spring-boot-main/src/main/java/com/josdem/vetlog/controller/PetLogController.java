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

import com.josdem.vetlog.command.PetLogCommand;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.service.LocaleService;
import com.josdem.vetlog.service.PetLogService;
import com.josdem.vetlog.service.PetService;
import com.josdem.vetlog.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import java.io.IOException;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.ModelAndView;

@Slf4j
@Controller
@RequestMapping("/petlog")
@RequiredArgsConstructor
public class PetLogController {

    public static final String PET_LOG_COMMAND = "petLogCommand";

    private final PetService petService;
    private final PetLogService petLogService;
    private final UserService userService;
    private final LocaleService localeService;

    @Value("${gcpUrl}")
    private String gcpUrl;

    @Value("${prescriptionBucket}")
    private String prescriptionBucket;

    @GetMapping(value = "/create")
    public ModelAndView create(@RequestParam("uuid") String uuid, HttpServletRequest request) {
        log.info("Pet uuid: {}", uuid);
        var modelAndView = new ModelAndView("petlog/create");
        var petLogCommand = new PetLogCommand();
        modelAndView.addObject(PET_LOG_COMMAND, petLogCommand);
        var pet = petService.getPetByUuid(uuid);
        var currentUser = userService.getCurrentUser();
        var pets = getPetsFromUser(pet, currentUser);
        return fillModelAndView(modelAndView, pets, request);
    }

    @PostMapping(value = "/save")
    public ModelAndView save(
            @Valid PetLogCommand petLogCommand, BindingResult bindingResult, HttpServletRequest request)
            throws IOException {
        log.info("Creating petLog: {}", petLogCommand.getPet());
        var modelAndView = new ModelAndView("petlog/create");
        var pet = petService.getPetById(petLogCommand.getPet());
        var currentUser = userService.getCurrentUser();
        var pets = getPetsFromUser(pet, currentUser);
        if (bindingResult.hasErrors()) {
            modelAndView.addObject(PET_LOG_COMMAND, petLogCommand);
            return fillModelAndView(modelAndView, pets, request);
        }
        petLogService.save(petLogCommand);
        modelAndView.addObject("message", localeService.getMessage("petlog.created", request));
        modelAndView.addObject(PET_LOG_COMMAND, new PetLogCommand());
        return fillModelAndView(modelAndView, pets, request);
    }

    private ModelAndView fillModelAndView(ModelAndView modelAndView, List<Pet> pets, HttpServletRequest request) {
        modelAndView.addObject("pets", pets);
        if (pets == null) {
            modelAndView.addObject("petListEmpty", localeService.getMessage("pet.list.empty", request));
        }
        return modelAndView;
    }

    @GetMapping(value = "/list")
    public ModelAndView list(@RequestParam("uuid") String uuid) {
        log.info("Listing pet logs");
        var modelAndView = new ModelAndView();
        var pet = petService.getPetByUuid(uuid);
        var petLogs = petLogService.getPetLogsByPet(pet);
        modelAndView.addObject("petLogs", petLogs);
        modelAndView.addObject("uuid", uuid);
        modelAndView.addObject("gcpPrescriptionUrl", gcpUrl + prescriptionBucket + "/");
        return modelAndView;
    }

    private List<Pet> getPetsFromUser(Pet pet, User currentUser) {
        List<Pet> pets;
        if (pet.getUser() == currentUser) {
            pets = petService.getPetsByUser(currentUser);
        } else {
            pets = petService.getPetsByUser(pet.getUser());
        }
        return pets;
    }
}
