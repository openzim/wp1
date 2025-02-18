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
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

import com.josdem.vetlog.enums.PetStatus;
import com.josdem.vetlog.enums.PetType;
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
class VetControllerTest {

    @Autowired
    private MockMvc mockMvc;

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
    @DisplayName("showing create vet form")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldShowCreateVetForm(TestInfo testInfo) throws Exception {
        log.info(testInfo.getDisplayName());
        mockMvc.perform(get("/vet/form"))
                .andExpect(status().isOk())
                .andExpect(model().attributeExists("usernameCommand"))
                .andExpect(view().name("vet/form"));
    }

    @Test
    @Transactional
    @DisplayName("searching by user")
    @WithMockUser(username = "admin", password = "12345678", roles = "ADMIN")
    void shouldSearchPetsByUser(TestInfo testInfo) throws Exception {
        log.info(testInfo.getDisplayName());

        registerPet();

        mockMvc.perform(post("/vet/search").with(csrf()).param("username", "josdem"))
                .andExpect(status().isOk())
                .andExpect(model().attributeExists("pets"))
                .andExpect(model().attributeExists("defaultImage"))
                .andExpect(view().name("vet/list"));
    }

    @Test
    @Transactional
    @DisplayName("searching by mobile")
    @WithMockUser(username = "admin", password = "12345678", roles = "ADMIN")
    void shouldSearchPetsByMobile(TestInfo testInfo) throws Exception {
        log.info(testInfo.getDisplayName());

        registerPet();

        mockMvc.perform(post("/vet/search").with(csrf()).param("username", "1234567890"))
                .andExpect(status().isOk())
                .andExpect(model().attributeExists("pets"))
                .andExpect(model().attributeExists("defaultImage"))
                .andExpect(view().name("vet/list"));
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
