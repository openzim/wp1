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

import com.josdem.vetlog.command.TelephoneCommand;
import com.josdem.vetlog.service.LocaleService;
import com.josdem.vetlog.service.PetService;
import com.josdem.vetlog.service.TelephoneService;
import com.josdem.vetlog.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Slf4j
@Controller
@RequestMapping("/telephone")
@RequiredArgsConstructor
public class TelephoneController {

    private final PetService petService;
    private final UserService userService;
    private final LocaleService localeService;
    private final TelephoneService telephoneService;

    @Value("${gcpUrl}")
    private String gcpUrl;

    @Value("${imageBucket}")
    private String imageBucket;

    @PostMapping(value = "/save")
    public ModelAndView save(
            @Valid TelephoneCommand telephoneCommand, BindingResult bindingResult, HttpServletRequest request) {
        log.info("Saving adoption for pet: {}", telephoneCommand.getUuid());
        if (bindingResult.hasErrors()) {
            ModelAndView modelAndView = new ModelAndView("telephone/adopt");
            modelAndView.addObject("errorMessage", localeService.getMessage("user.error.mobile", request));
            return fillPetAndTelephoneCommand(modelAndView, telephoneCommand);
        }
        var user = userService.getCurrentUser();
        telephoneService.save(telephoneCommand, user);
        var modelAndView = new ModelAndView("redirect:/");
        modelAndView.addObject("message", localeService.getMessage("adoption.email.sent", request));
        return modelAndView;
    }

    @GetMapping(value = "/adopt")
    public ModelAndView adopt(TelephoneCommand telephoneCommand) {
        log.info("Adoption to pet with uuid: {}", telephoneCommand.getUuid());
        var modelAndView = new ModelAndView("telephone/adopt");
        return fillPetAndTelephoneCommand(modelAndView, telephoneCommand);
    }

    private ModelAndView fillPetAndTelephoneCommand(ModelAndView modelAndView, TelephoneCommand telephoneCommand) {
        var pet = petService.getPetByUuid(telephoneCommand.getUuid());
        modelAndView.addObject("pet", pet);
        modelAndView.addObject("telephoneCommand", telephoneCommand);
        modelAndView.addObject("gcpImageUrl", gcpUrl + imageBucket + "/");
        return modelAndView;
    }
}
