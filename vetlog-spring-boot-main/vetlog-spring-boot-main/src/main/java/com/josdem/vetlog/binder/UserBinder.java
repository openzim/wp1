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

package com.josdem.vetlog.binder;

import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.UserCommand;
import com.josdem.vetlog.enums.Role;
import com.josdem.vetlog.model.User;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class UserBinder {

    public User bindUser(Command command) {
        UserCommand userCommand = (UserCommand) command;
        User user = new User();
        user.setUsername(userCommand.getUsername());
        user.setPassword(new BCryptPasswordEncoder().encode(userCommand.getPassword()));
        user.setRole(Role.USER);
        user.setFirstName(userCommand.getFirstname());
        user.setLastName(userCommand.getLastname());
        user.setCountryCode(userCommand.getCountryCode());
        user.setMobile(userCommand.getMobile());
        user.setEmail(userCommand.getEmail());
        return user;
    }
}
