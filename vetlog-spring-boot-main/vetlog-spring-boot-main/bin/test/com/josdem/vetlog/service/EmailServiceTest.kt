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

package com.josdem.vetlog.service

import com.josdem.vetlog.config.TemplateProperties
import com.josdem.vetlog.exception.BusinessException
import com.josdem.vetlog.model.User
import com.josdem.vetlog.service.impl.EmailServiceImpl
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.assertThrows
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.slf4j.LoggerFactory
import java.io.IOException
import kotlin.test.Test

internal class EmailServiceTest {

    private lateinit var emailService: EmailService

    @Mock
    private lateinit var restService: RestService

    @Mock
    private lateinit var localeService: LocaleService

    @Mock
    private lateinit var templateProperties: TemplateProperties

    private val user = User()

    companion object {
        private val log = LoggerFactory.getLogger(EmailServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        emailService = EmailServiceImpl(restService, localeService, templateProperties)
    }

    @Test
    fun `Sending a welcome email`() {
        log.info("Running test: Sending a welcome email")
        whenever(templateProperties.welcome).thenReturn("welcome.ftl")
        user.firstName = "Jose"
        user.email = "contact@josdem.io"

        emailService.sendWelcomeEmail(user)

        verify(localeService).getMessage("user.welcome.message")
        verify(restService).sendMessage(any())
    }

    @Test
    fun `Not sending a welcome email due to an exception`() {
        log.info("Running test: Not sending a welcome email due to an exception")
        whenever(restService.sendMessage(any())).thenThrow(IOException("Error"))

        assertThrows<BusinessException> {
            emailService.sendWelcomeEmail(user)
        }
    }

    @Test
    fun `Not sending email if user is not enabled`() {
        log.info("Running test: Not sending email if user is not enabled")
        user.isEnabled = false

        emailService.sendWelcomeEmail(user)

        verify(restService, never()).sendMessage(any())
    }
}