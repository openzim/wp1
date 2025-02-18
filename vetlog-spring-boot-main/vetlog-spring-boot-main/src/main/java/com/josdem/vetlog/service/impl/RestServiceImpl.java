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

import com.josdem.vetlog.command.MessageCommand;
import com.josdem.vetlog.service.RestService;
import java.io.IOException;
import javax.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.ResponseBody;
import org.springframework.stereotype.Service;
import retrofit2.Call;
import retrofit2.Retrofit;
import retrofit2.http.Body;

@Slf4j
@Service
@RequiredArgsConstructor
public class RestServiceImpl implements RestService {

    private final Retrofit retrofit;
    private RestService restService;

    @PostConstruct
    public void setup() {
        restService = retrofit.create(RestService.class);
    }

    @Override
    public Call<ResponseBody> sendMessage(@Body MessageCommand command) throws IOException {
        var call = restService.sendMessage(command);
        call.execute();
        return call;
    }
}
