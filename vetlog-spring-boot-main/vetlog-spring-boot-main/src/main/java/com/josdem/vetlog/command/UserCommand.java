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

package com.josdem.vetlog.command;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UserCommand implements Command {

    @Size(min = 6, max = 50)
    private String username;

    @Size(min = 8, max = 50)
    private String password;

    @Size(min = 8, max = 50)
    private String passwordConfirmation;

    @Size(min = 1, max = 50)
    private String firstname;

    @Size(min = 1, max = 100)
    private String lastname;

    @Size(min = 10, max = 10)
    private String mobile;

    @Size(min = 1, max = 5)
    private String countryCode;

    @Email
    @Size(min = 1, max = 250)
    private String email;
}
