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

package com.josdem.vetlog.service.impl;

import com.josdem.vetlog.client.GoogleStorageWriter;
import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.PetCommand;
import com.josdem.vetlog.model.PetImage;
import com.josdem.vetlog.repository.PetImageRepository;
import com.josdem.vetlog.service.PetImageService;
import com.josdem.vetlog.util.UuidGenerator;
import java.io.IOException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PetImageServiceImpl implements PetImageService {

    public static final String CONTENT_TYPE = "image/jpeg";

    private final PetImageRepository petImageRepository;
    private final GoogleStorageWriter googleStorageWriter;

    @Value("${imageBucket}")
    private String bucket;

    private PetImage save() {
        var petImage = new PetImage();
        petImage.setUuid(UuidGenerator.generateUuid());
        petImageRepository.save(petImage);
        return petImage;
    }

    public void attachFile(Command command) throws IOException {
        var petCommand = (PetCommand) command;
        if (petCommand.getImage() == null) {
            return;
        }
        if (petCommand.getImage().getInputStream().available() > 0) {
            var petImage = save();
            petCommand.getImages().add(petImage);
            googleStorageWriter.uploadToBucket(
                    bucket, petImage.getUuid(), petCommand.getImage().getInputStream(), CONTENT_TYPE);
        }
    }
}
