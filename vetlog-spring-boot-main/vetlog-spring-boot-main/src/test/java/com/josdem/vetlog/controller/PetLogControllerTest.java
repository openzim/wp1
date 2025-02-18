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

import static com.josdem.vetlog.controller.PetControllerTest.PET_UUID;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

import com.josdem.vetlog.enums.PetStatus;
import com.josdem.vetlog.enums.PetType;
import com.josdem.vetlog.repository.PetRepository;
import jakarta.transaction.Transactional;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

@Slf4j
@SpringBootTest
@AutoConfigureMockMvc
class PetLogControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private PetRepository petRepository;

    @Autowired
    private WebApplicationContext webApplicationContext;

    private final MockMultipartFile image =
            new MockMultipartFile("mockImage", "image.jpg", "image/jpeg", "image".getBytes());

    @BeforeEach
    public void setUp() {
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext)
                .apply(springSecurity())
                .build();
    }

    @Test
    @Transactional
    @DisplayName("showing create pet log form")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldShowCreatePetLogForm(TestInfo testInfo) throws Exception {
        log.info("Running: {}", testInfo.getDisplayName());

        registerPet();

        mockMvc.perform(get("/petlog/create").param("uuid", PET_UUID))
                .andExpect(status().isOk())
                .andExpect(model().attributeExists("petLogCommand"))
                .andExpect(view().name("petlog/create"));
    }

    @Test
    @Transactional
    @DisplayName("registering a pet log")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldRegisterPetLog(TestInfo testInfo) throws Exception {
        log.info("Running: {}", testInfo.getDisplayName());

        registerPet();

        var cremita = petRepository.findByUuid(PET_UUID).orElseThrow(() -> new RuntimeException("Pet not found"));

        mockMvc.perform(MockMvcRequestBuilders.multipart("/petlog/save")
                        .with(csrf())
                        .param("pet", cremita.getId().toString())
                        .param("uuid", PET_UUID)
                        .param("date", "2024-09-27")
                        .param("description", "description")
                        .param("diagnosis", "diagnosis")
                        .param("signs", "signs"))
                .andExpect(status().isOk())
                .andExpect(view().name("petlog/create"));
    }

    @Test
    @DisplayName("not listing pet logs due to uuid not found")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldNotListPetLogs(TestInfo testInfo) throws Exception {
        log.info("Running: {}", testInfo.getDisplayName());
        mockMvc.perform(get("/petlog/list").param("uuid", "uuid"))
                .andExpect(status().isOk())
                .andExpect(view().name("error"));
    }

    @Test
    @Transactional
    @DisplayName("listing pet logs")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldListPetLogs(TestInfo testInfo) throws Exception {
        log.info("Running: {}", testInfo.getDisplayName());

        registerPet();

        mockMvc.perform(get("/petlog/list").param("uuid", PET_UUID))
                .andExpect(status().isOk())
                .andExpect(model().attributeExists("petLogs"))
                .andExpect(model().attributeExists("uuid"))
                .andExpect(view().name("petlog/list"));
    }

    private void registerPet() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.multipart("/pet/save")
                        .file(image)
                        .with(csrf())
                        .param("name", "Cremita")
                        .param("uuid", PET_UUID)
                        .param("birthDate", "2024-08-22")
                        .param("dewormed", "true")
                        .param("vaccinated", "true")
                        .param("sterilized", "true")
                        .param("breed", "11")
                        .param("user", "1")
                        .param("status", PetStatus.OWNED.toString())
                        .param("type", PetType.DOG.toString()))
                .andExpect(status().isOk())
                .andExpect(view().name("pet/create"));
    }
}
