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

import com.josdem.vetlog.util.UuidGenerator;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.springframework.web.multipart.MultipartFile;

@Getter
@Setter
@ToString
public class PetLogCommand implements Command {
    @Size(max = 200)
    private String vetName;

    @Size(min = 1, max = 1000)
    private String signs;

    @Size(min = 1, max = 1000)
    private String diagnosis;

    @Size(min = 1, max = 1000)
    private String medicine;

    private String uuid = UuidGenerator.generateUuid();

    @Min(1L)
    private Long pet;

    private transient MultipartFile attachment;
}
