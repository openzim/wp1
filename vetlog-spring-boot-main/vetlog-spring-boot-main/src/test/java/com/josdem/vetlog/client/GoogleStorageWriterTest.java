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

package com.josdem.vetlog.client;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.api.gax.core.CredentialsProvider;
import com.google.auth.Credentials;
import com.google.cloud.spring.core.GcpProjectIdProvider;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.helper.StorageOptionsHelper;
import java.io.IOException;
import java.io.InputStream;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

@Slf4j
class GoogleStorageWriterTest {

    private GoogleStorageWriter googleStorageWriter;

    @Mock
    private CredentialsProvider credentialsProvider;

    @Mock
    private GcpProjectIdProvider gcpProjectIdProvider;

    @Mock
    private StorageOptionsHelper storageOptionsHelper;

    @Mock
    private InputStream inputStream;

    @Mock
    private Storage storage;

    @Mock
    private Credentials credentials;

    @Mock
    private StorageOptions storageOptions;

    @Mock
    private StorageOptions.Builder builder;

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
        googleStorageWriter = new GoogleStorageWriter(credentialsProvider, gcpProjectIdProvider, storageOptionsHelper);
    }

    @Test
    @DisplayName("Should upload to bucket")
    void shouldUploadToBucket(TestInfo testInfo) throws Exception {
        log.info(testInfo.getDisplayName());

        setExpectations();

        googleStorageWriter.setup();
        googleStorageWriter.uploadToBucket("bucket", "fileName", inputStream, "contentType");
        verify(inputStream).readAllBytes();
    }

    @Test
    @DisplayName("not upload to bucket due to exception")
    void shouldNotUploadToBucket(TestInfo testInfo) throws Exception {
        log.info(testInfo.getDisplayName());

        setExpectations();

        googleStorageWriter.setup();
        when(inputStream.readAllBytes()).thenThrow(new IllegalStateException("Error"));
        assertThrows(
                BusinessException.class,
                () -> googleStorageWriter.uploadToBucket("bucket", "fileName", inputStream, "contentType"));
    }

    private void setExpectations() throws IOException {
        when(gcpProjectIdProvider.getProjectId()).thenReturn("projectId");
        when(credentialsProvider.getCredentials()).thenReturn(credentials);

        when(storageOptionsHelper.getStorageOptions()).thenReturn(builder);
        when(builder.setProjectId("projectId")).thenReturn(builder);
        when(builder.setCredentials(credentials)).thenReturn(builder);
        when(builder.build()).thenReturn(storageOptions);
        when(builder.build().getService()).thenReturn(storage);
    }
}
