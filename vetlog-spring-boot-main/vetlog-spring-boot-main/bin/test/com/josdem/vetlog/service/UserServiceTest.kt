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

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse

import com.josdem.vetlog.binder.UserBinder
import com.josdem.vetlog.command.Command
import com.josdem.vetlog.config.ApplicationProperties
import com.josdem.vetlog.exception.UserNotFoundException
import com.josdem.vetlog.model.User
import com.josdem.vetlog.repository.UserRepository
import com.josdem.vetlog.service.impl.UserServiceImpl
import com.josdem.vetlog.util.UserContextHolderProvider

import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo
import org.junit.jupiter.api.assertThrows
import org.mockito.Mock
import org.mockito.Mockito.mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.slf4j.LoggerFactory
import org.springframework.security.core.Authentication
import kotlin.test.Test
import java.util.Optional

internal class UserServiceTest {
    private lateinit var service: UserService
    private val user = User()

    @Mock
    private lateinit var userBinder: UserBinder

    @Mock
    private lateinit var userRepository: UserRepository

    @Mock
    private lateinit var provider: UserContextHolderProvider

    @Mock
    private lateinit var applicationProperties: ApplicationProperties

    @Mock
    private lateinit var emailService: EmailService

    companion object {
        private val log = LoggerFactory.getLogger(UserServiceTest::class.java)
        private const val USERNAME = "josdem"
        private const val EMAIL = "contact@josdem.io"
        private const val MOBILE = "+521234567890"
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = UserServiceImpl(userBinder, userRepository, provider, applicationProperties, emailService)
    }

    @Test
    fun `Getting user by username`() {
        log.info("Running test: Getting user by username")
        whenever(userRepository.findByUsername(USERNAME)).thenReturn(Optional.of(user))
        val result = service.getByUsername(USERNAME)
        assertEquals(user, result)
    }

    @Test
    fun `Not finding user by username`() {
        log.info("Running test: Not finding user by username")
        whenever(userRepository.findByUsername(USERNAME)).thenReturn(Optional.empty())
        assertThrows<UserNotFoundException> { service.getByUsername(USERNAME) }
    }

    @Test
    fun `Getting user by email`() {
        log.info("Running test: Getting user by email")
        whenever(userRepository.findByEmail(EMAIL)).thenReturn(Optional.of(user))
        val result = service.getByEmail(EMAIL)
        assertEquals(user, result)
    }

    @Test
    fun `Not finding user by email`() {
        log.info("Running test: Not finding user by email")
        whenever(userRepository.findByEmail(EMAIL)).thenReturn(Optional.empty())
        assertThrows<UserNotFoundException> { service.getByEmail(EMAIL) }
    }

    @Test
    fun `Saving a user`() {
        log.info("Running test: Saving a user")
        val command: Command = mock()
        user.email = EMAIL
        whenever(userBinder.bindUser(command)).thenReturn(user)

        val result = service.save(command)

        verify(emailService).sendWelcomeEmail(user)
        verify(userRepository).save(user)
        assertEquals(user, result)
    }

    @Test
    fun `Disabling a user due to country code`() {
        log.info("Running test: Disabling a user due to country code")
        val command: Command = mock()
        user.email = EMAIL
        user.countryCode = "+countryCodeOne"
        whenever(applicationProperties.countryCodes).thenReturn(mutableListOf("+countryCodeOne"))
        whenever(userBinder.bindUser(command)).thenReturn(user)

        val result = service.save(command)

        verify(userRepository).save(user)
        assertEquals(user, result)
        assertFalse(user.isEnabled, "User should be disabled")
    }

    @Test
    fun `Getting current user`() {
        log.info("Running test: Getting current user")
        val authentication: Authentication = mock()
        whenever(authentication.name).thenReturn(USERNAME)
        whenever(provider.authentication).thenReturn(authentication)
        whenever(userRepository.findByUsername(USERNAME)).thenReturn(Optional.of(user))
        assertEquals(user, service.getCurrentUser())
    }

    @Test
    fun `Not finding current user`() {
        log.info("Running test: Not finding current user")
        val authentication: Authentication = mock()
        whenever(authentication.name).thenReturn(USERNAME)
        whenever(provider.authentication).thenReturn(authentication)
        whenever(userRepository.findByUsername(USERNAME)).thenReturn(Optional.empty())
        assertThrows<UserNotFoundException> { service.getCurrentUser() }
    }

    @Test
    fun `Should find an user by mobile`(testInfo: TestInfo) {
        log.info(testInfo.displayName)
        whenever(userRepository.findByMobile(MOBILE)).thenReturn(Optional.of(user))
        val result = service.getByMobile(MOBILE)
        assertEquals(user, result)
    }

    @Test
    fun `Should not find an user by mobile`(testInfo: TestInfo) {
        log.info(testInfo.displayName)
        assertThrows<UserNotFoundException> { service.getByMobile(MOBILE) }
    }
}
