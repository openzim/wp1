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
class AdoptionControllerTest {

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
    @Transactional
    @DisplayName("showing description for adoption form")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldShowDescriptionForAdoptionForm() throws Exception {

        registerPet();

        mockMvc.perform(get("/adoption/descriptionForAdoption").param("uuid", PET_UUID))
                .andExpect(status().isOk())
                .andExpect(view().name("adoption/descriptionForAdoption"))
                .andExpect(model().attributeExists("pet"))
                .andExpect(model().attributeExists("adoptionCommand"))
                .andExpect(status().isOk());
    }

    @Test
    @Transactional
    @DisplayName("saving adoption description")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldSaveAdoptionDescription(TestInfo testInfo) throws Exception {
        log.info("Running: {}", testInfo.getDisplayName());

        registerPet();

        mockMvc.perform(post("/adoption/save")
                        .with(csrf())
                        .param("uuid", PET_UUID)
                        .param("description", "Cremita is a lovely dog")
                        .param("status", PetStatus.IN_ADOPTION.toString()))
                .andExpect(status().isOk())
                .andExpect(view().name("pet/listForAdoption"));
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
