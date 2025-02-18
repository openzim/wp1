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

import com.josdem.vetlog.enums.PetStatus;
import com.josdem.vetlog.enums.PetType;
import com.josdem.vetlog.model.PetImage;
import com.josdem.vetlog.model.Vaccination;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.ArrayList;
import java.util.List;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.springframework.web.multipart.MultipartFile;

@Getter
@Setter
@ToString
public class PetCommand implements Command {

    private Long id;

    @Size(min = 1, max = 50)
    private String name;

    @NotNull
    private String birthDate;

    private Boolean dewormed = false;

    private Boolean sterilized = false;

    private Boolean vaccinated = false;

    @Min(1L)
    private Long breed;

    @Min(1L)
    private Long user;

    @Min(1L)
    private Long adopter;

    @NotNull
    private PetType type;

    private String uuid;

    private PetStatus status;

    private transient MultipartFile image;

    private transient List<PetImage> images = new ArrayList<>();

    private transient List<Vaccination> vaccines = new ArrayList<>();

    public void defaultBirthDateAndTime() {
        this.birthDate = birthDate + "T" + "06:00";
    }
}
