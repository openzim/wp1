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

import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.UserCommand;
import com.josdem.vetlog.service.LocaleService;
import com.josdem.vetlog.service.UserService;
import com.josdem.vetlog.validator.UserValidator;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.InitBinder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Slf4j
@Controller
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserValidator userValidator;
    private final UserService userService;
    private final LocaleService localeService;

    @InitBinder("userCommand")
    private void initBinder(WebDataBinder binder) {
        binder.addValidators(userValidator);
    }

    @GetMapping(value = "/create")
    public ModelAndView create() {
        return fillUserCommand(new UserCommand());
    }

    @PostMapping(value = "/save")
    public ModelAndView save(@Valid UserCommand userCommand, BindingResult bindingResult, HttpServletRequest request) {
        log.info("Saving user: {}", userCommand.getUsername());
        if (bindingResult.hasErrors()) {
            return fillUserCommand(userCommand);
        }
        userService.save(userCommand);
        var modelAndView = new ModelAndView("login/login");
        modelAndView.addObject("userAccountCreatedMessage", localeService.getMessage("user.account.created", request));
        return modelAndView;
    }

    private ModelAndView fillUserCommand(Command userCommand) {
        var modelAndView = new ModelAndView("user/create");
        modelAndView.addObject("userCommand", userCommand);
        return modelAndView;
    }
}
