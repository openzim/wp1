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
class TelephoneControllerTest {

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
    @DisplayName("showing adopting form")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldShowAdoptingForm(TestInfo testInfo) throws Exception {

        registerPet();

        log.info("Running: {}", testInfo.getDisplayName());
        mockMvc.perform(get("/telephone/adopt").param("uuid", PET_UUID))
                .andExpect(status().isOk())
                .andExpect(view().name("telephone/adopt"))
                .andExpect(model().attributeExists("pet"))
                .andExpect(model().attributeExists("telephoneCommand"))
                .andExpect(status().isOk());
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

    @Test
    @Transactional
    @DisplayName("not saving adoption due to invalid phone number")
    @WithMockUser(username = "josdem", password = "12345678", roles = "USER")
    void shouldNotSaveAdoption(TestInfo testInfo) throws Exception {
        registerPet();

        log.info(testInfo.getDisplayName());
        mockMvc.perform(post("/telephone/save")
                        .with(csrf())
                        .param("uuid", PET_UUID)
                        .param("mobile", "123"))
                .andExpect(status().isOk())
                .andExpect(view().name("telephone/adopt"))
                .andExpect(model().attributeExists("pet"))
                .andExpect(model().attributeExists("telephoneCommand"))
                .andExpect(status().isOk());
    }
}
