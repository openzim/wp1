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
import com.josdem.vetlog.command.PetLogCommand;
import com.josdem.vetlog.service.PetPrescriptionService;
import java.io.IOException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PetPrescriptionServiceImpl implements PetPrescriptionService {

    public static final String CONTENT_TYPE = "application/octet-stream";
    private final GoogleStorageWriter googleStorageWriter;

    @Value("${prescriptionBucket}")
    private String bucket;

    public void attachFile(Command command) throws IOException {
        var petLogCommand = (PetLogCommand) command;
        if (petLogCommand.getAttachment() == null) {
            return;
        }
        if (petLogCommand.getAttachment().getInputStream().available() > 0) {
            googleStorageWriter.uploadToBucket(
                    bucket,
                    petLogCommand.getUuid(),
                    petLogCommand.getAttachment().getInputStream(),
                    CONTENT_TYPE);
        }
    }
}
