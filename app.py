[     UTC     ] Logs for autointel-ai-h9qcsgyuappcasimqslgsdj.streamlit.app/

────────────────────────────────────────────────────────────────────────────────────────

[08:46:25] 🚀 Starting up repository: 'autointel-ai', branch: 'main', main module: 'app.py'

[08:46:25] 🐙 Cloning repository...

[08:46:26] 🐙 Cloning into '/mount/src/autointel-ai'...

[08:46:26] 🐙 Cloned repository!

[08:46:26] 🐙 Pulling code changes from Github...

[08:46:26] 📦 Processing dependencies...


──────────────────────────────────────── uv ───────────────────────────────────────────


Using uv pip install.

Using Python 3.12.10 environment at /home/adminuser/venv

Resolved 59 packages in 1.23s

Prepared [2025-04-26 08:46:34.690210] 59 packages[2025-04-26 08:46:34.690748]  [2025-04-26 08:46:34.691278] in 5.93s[2025-04-26 08:46:34.691808] 

Installed 59 packages in 192ms

 + altair==5.5.0

 + annotated-types==0.7.0

 + anyio==4.9.0

 + apscheduler==3.11.0

 + attrs==25.3.0

 + beautifulsoup4==4.12.3

 + blinker==1.9.0

 +[2025-04-26 08:46:34.886035]  cachetools==5.5.2

 + certifi==2025.4.26

 + charset-normalizer==3.4.1

 + click==8.1.8

 + distro==1.9.0

 + gitdb==4.0.12

 + gitpython==3.1.44

 + greenlet==3.2.1

 + h11[2025-04-26 08:46:34.886390] ==0.16.0

 + httpcore==1.0.9

 + httpx[2025-04-26 08:46:34.886649] ==0.28.1

 + idna==3.10

 + [2025-04-26 08:46:34.886858] jinja2==3.1.6

 + jiter==0.9.0

 + jsonschema==4.23.0

 + jsonschema-specifications==[2025-04-26 08:46:34.887800] 2025.4.1

 + lxml==5.4.0

 [2025-04-26 08:46:34.888084] + markupsafe==3.0.2

 + narwhals==[2025-04-26 08:46:34.888307] 1.36.0

 + numpy==1.26.4

 + openai==1.76.0

 + packaging[2025-04-26 08:46:34.888549] ==24.2

 + pandas==2.2.3

 + pillow==11.2.1

 +[2025-04-26 08:46:34.888785]  playwright==1.50.0

 + protobuf==5.29.4

 + pyarrow==19.0.1

 [2025-04-26 08:46:34.888992] + pydantic==2.11.3

 + pydantic-core==2.33.1

 + pydeck==0.9.1

 + pyee==12.1.1[2025-04-26 08:46:34.889189] 

 + python-dateutil==2.9.0.post0

 + python-dotenv==1.0.1

 + pytz==2025.2

 + referencing==0.36.2

 + requests==2.32.3

 + rpds-py==[2025-04-26 08:46:34.889391] 0.24.0

 + six==1.17.0

 + smmap==5.0.2

 + sniffio==1.3.1

 + soupsieve==2.7

 + streamlit==1.44.0

 + tenacity==9.1.2[2025-04-26 08:46:34.889607] 

 + toml==0.10.2

 + tornado==6.4.2

 + tqdm==4.66.5

 + typing-extensions==4.13.2

 + typing-inspection==0.4.0

 +[2025-04-26 08:46:34.889748]  tzdata==2025.2

 + tzlocal==5.3.1

 + urllib3==2.4.0

 + watchdog==6.0.0

Checking if Streamlit is installed

Found Streamlit version 1.44.0 in the environment

Installing rich for an improved exception logging

Using uv pip install.

Using Python 3.12.10 environment at /home/adminuser/venv

Resolved 4 packages in 157ms

Prepared 4 packages in 173ms

Installed 4 packages in 27ms

 + markdown-it-py==3.0.0

 + mdurl==0.1.2

 + pygments==2.19.1

 + rich==14.0.0


────────────────────────────────────────────────────────────────────────────────────────


[08:46:37] 🐍 Python dependencies were installed from /mount/src/autointel-ai/requirements.txt using uv.

Check if streamlit is installed

Streamlit is already installed

[08:46:39] 📦 Processed dependencies!




2025-04-26 08:46:54.041 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 549, in _run_script

    code = self._script_cache.get_bytecode(script_path)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/magic.py", line 46, in add_magic

    tree = ast.parse(code, script_path, "exec")

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/ast.py", line 52, in parse

    return compile(source, filename, mode, flags,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/autointel-ai/app.py", line 326

    if __name__ == "__main__":

                              ^

IndentationError: expected an indented block after 'if' statement on line 326

2025-04-26 08:46:54.044 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

[08:49:05] 🐙 Pulling code changes from Github...

2025-04-26 08:49:05.954 Received event for non-watched file: /mount/src/autointel-ai/app.py

[08:49:06] 📦 Processing dependencies...

[08:49:06] 📦 Processed dependencies!

[08:49:10] 🔄 Updated app!

────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:625 in _to_bytes                                                   

                                                                                

  /usr/local/lib/python3.12/copyreg.py:70 in _reduce_ex                         

                                                                                

     67 │   │   state = None                                                    

     68 │   else:                                                               

     69 │   │   if base is cls:                                                 

  ❱  70 │   │   │   raise TypeError(f"cannot pickle {cls.__name__!r} object")   

     71 │   │   state = base(self)                                              

     72 │   args = (cls, base, state)                                           

     73 │   try:                                                                

────────────────────────────────────────────────────────────────────────────────

TypeError: cannot pickle 'function' object


The above exception was the direct cause of the following exception:


────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:450 in _make_value_key                                         

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:162 in update_hash                                                 

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:345 in update                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:327 in to_bytes                                                    

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:630 in _to_bytes                                                   

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:345 in update                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:327 in to_bytes                                                    

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:627 in _to_bytes                                                   

────────────────────────────────────────────────────────────────────────────────

UnhashableTypeError


During handling of the above exception, another exception occurred:


────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:121 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:640 in code_to_exec                                     

                                                                                

  /mount/src/autointel-ai/app.py:327 in <module>                                

                                                                                

    324                                                                         

    325                                                                         

    326 if __name__ == "__main__":                                              

  ❱ 327 │   main()                                                              

    328                                                                         

                                                                                

  /mount/src/autointel-ai/app.py:271 in main                                    

                                                                                

    268 │   # --- Deal Alerts ---                                               

    269 │   with tabs[3]:                                                       

    270 │   │   st.header("Deal Alerts")                                        

  ❱ 271 │   │   sample = generator.generate_listings(5)                         

    272 │   │   opts = [                                                        

    273 │   │   │   f"{c.year} {c.make} {c.model} — ${c.price:,.0f}"            

    274 │   │   │   for c in sample                                             

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:175 in __call__                                                

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:219 in __call__                                                

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:234 in _get_or_create_cached_value                             

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:458 in _make_value_key                                         

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  cache_utils.py:450 in _make_value_key                                         

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:162 in update_hash                                                 

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:345 in update                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:327 in to_bytes                                                    

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:630 in _to_bytes                                                   

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:345 in update                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:327 in to_bytes                                                    

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/  

  hashing.py:627 in _to_bytes                                                   

────────────────────────────────────────────────────────────────────────────────

UnhashableParamError: Cannot hash argument 'self' (of type 

`__main__.ListingGenerator`) in 'generate_listings'.


To address this, you can tell Streamlit not to hash this argument by adding a

leading underscore to the argument's name in the function signature:


```

@st.cache_data

def generate_listings(_self, ...):

    ...

```

            

[08:51:12] 🐙 Pulling code changes from Github...

[08:51:13] 📦 Processing dependencies...

[08:51:13] 📦 Processed dependencies!

[08:51:15] 🔄 Updated app!

2025-04-26 08:51:27,548 INFO AutoIntelAI: Sending code to GPT-4 for review.

2025-04-26 08:51:27,548 ERROR AutoIntelAI: OpenAI API call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 171, in review_code

    response = openai.ChatCompletion.create(

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


2025-04-26 08:51:44,815 INFO AutoIntelAI: Sending code to GPT-4 for review.

2025-04-26 08:51:44,815 ERROR AutoIntelAI: OpenAI API call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 171, in review_code

    response = openai.ChatCompletion.create(

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


2025-04-26 08:58:32,268 INFO AutoIntelAI: Sending code to GPT-4 for review.

2025-04-26 08:58:32,268 ERROR AutoIntelAI: OpenAI API call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 171, in review_code

    response = openai.ChatCompletion.create(

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


2025-04-26 08:58:38,169 INFO AutoIntelAI: Sending code to GPT-4 for review.

2025-04-26 08:58:38,170 ERROR AutoIntelAI: OpenAI API call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 171, in review_code

    response = openai.ChatCompletion.create(

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


[09:00:25] 🐙 Pulling code changes from Github...

[09:00:26] 📦 Processing dependencies...

[09:00:26] 📦 Processed dependencies!

[09:00:28] 🔄 Updated app!

2025-04-26 09:00:30,783 ERROR AutoIntelAI: AI Assistant call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 204, in get_ai_assistant_response

    resp = openai.ChatCompletion.create(

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


2025-04-26 09:00:46,775 ERROR AutoIntelAI: AI Assistant call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 204, in get_ai_assistant_response

    resp = openai.ChatCompletion.create(

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


2025-04-26 09:00:54,991 INFO AutoIntelAI: Sending code to GPT-4 for review.

2025-04-26 09:00:54,992 ERROR AutoIntelAI: OpenAI API call failed.

Traceback (most recent call last):

  File "/mount/src/autointel-ai/app.py", line 166, in review_code

    response = openai.ChatCompletion.create(

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py", line 39, in __call__

    raise APIRemovedInV1(symbol=self._symbol)

openai.lib._old_api.APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`


A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742


[09:02:25] 🐙 Pulling code changes from Github...

2025-04-26 09:02:25.933 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 549, in _run_script

    code = self._script_cache.get_bytecode(script_path)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/magic.py", line 46, in add_magic

    tree = ast.parse(code, script_path, "exec")

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/ast.py", line 52, in parse

    return compile(source, filename, mode, flags,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/autointel-ai/app.py", line 1

    ```python

    ^

SyntaxError: invalid syntax

2025-04-26 09:02:25.935 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

[09:02:25] 📦 Processing dependencies...

[09:02:25] 📦 Processed dependencies!

[09:02:27] 🔄 Updated app!

2025-04-26 09:02:33.754 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 549, in _run_script

    code = self._script_cache.get_bytecode(script_path)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/magic.py", line 46, in add_magic

    tree = ast.parse(code, script_path, "exec")

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/ast.py", line 52, in parse

    return compile(source, filename, mode, flags,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/autointel-ai/app.py", line 1

    ```python

    ^

SyntaxError: invalid syntax

2025-04-26 09:02:33.755 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

[09:04:15] 🐙 Pulling code changes from Github...

2025-04-26 09:04:16.404 Received event for non-watched file: /mount/src/autointel-ai/app.py

[09:04:16] 📦 Processing dependencies...

[09:04:16] 📦 Processed dependencies!

[09:04:18] 🔄 Updated app!

────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:121 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:640 in code_to_exec                                     

                                                                                

  /mount/src/autointel-ai/app.py:160 in <module>                                

                                                                                

    157 │   │   if st.button("Analyze Code"): st.write(reviewer.review_code(co  

    158                                                                         

    159 if __name__=="__main__":                                                

  ❱ 160 │   main()                                                              

    161                                                                         

    162                                                                         

                                                                                

  /mount/src/autointel-ai/app.py:139 in main                                    

                                                                                

    136 │                                                                       

    137 │   with tabs[1]:                                                       

    138 │   │   q = st.text_input("Ask:")                                       

  ❱ 139 │   │   if st.button("Ask AI", key="ask"): st.write(get_ai_assistant_r  

    140 │                                                                       

    141 │   with tabs[2]:                                                       

    142 │   │   vin = st.text_input("VIN:")                                     

                                                                                

  /mount/src/autointel-ai/app.py:118 in get_ai_assistant_response               

                                                                                

    115 │   │   return "Prices update often—see Track Listings."                

    116 │   if "mileage" in low:                                                

    117 │   │   return "Lower mileage often means higher value."                

  ❱ 118 │   resp = openai.ChatCompletion.create(model=AppConfig.OPENAI_MODEL,   

    119 │   return resp.choices[0].message.content.strip()                      

    120                                                                         

    121 # 9. UI & MAIN                                                          

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/lib/_old_api.py:39   

  in __call__                                                                   

                                                                                

    36 │   │   return self                                                      

    37 │                                                                        

    38 │   def __call__(self, *_args: Any, **_kwargs: Any) -> Any:              

  ❱ 39 │   │   raise APIRemovedInV1(symbol=self._symbol)                        

    40                                                                          

    41                                                                          

    42 SYMBOLS = [                                                              

────────────────────────────────────────────────────────────────────────────────

APIRemovedInV1: 


You tried to access openai.ChatCompletion, but this is no longer supported in 

openai>=1.0.0 - see the README at https://github.com/openai/openai-python for 

the API.


You can run `openai migrate` to automatically upgrade your codebase to use the 

1.0.0 interface. 


Alternatively, you can pin your installation to the old version, e.g. `pip 

install openai==0.28`


A detailed migration guide is available here: 

https://github.com/openai/openai-python/discussions/742


[09:06:13] 🐙 Pulling code changes from Github...

[09:06:14] 📦 Processing dependencies...

[09:06:14] 📦 Processed dependencies!

[09:06:15] 🔄 Updated app!

────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:121 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:640 in code_to_exec                                     

                                                                                

  /mount/src/autointel-ai/app.py:167 in <module>                                

                                                                                

    164 │   │   │   st.write(reviewer.review_code(code_text))                   

    165                                                                         

    166 if __name__ == "__main__":                                              

  ❱ 167 │   main()                                                              

    168                                                                         

                                                                                

  /mount/src/autointel-ai/app.py:143 in main                                    

                                                                                

    140 │   with tabs[1]:                                                       

    141 │   │   q = st.text_input("Ask:")                                       

    142 │   │   if st.button("Ask AI", key="ask"):                              

  ❱ 143 │   │   │   st.write(get_ai_assistant_response(q))                      

    144 │                                                                       

    145 │   with tabs[2]:                                                       

    146 │   │   vin = st.text_input("VIN:")                                     

                                                                                

  /mount/src/autointel-ai/app.py:118 in get_ai_assistant_response               

                                                                                

    115 │   │   return "Prices update often—see Track Listings."                

    116 │   if "mileage" in low:                                                

    117 │   │   return "Lower mileage often means higher value."                

  ❱ 118 │   response = openai.chat.completions.create(                          

    119 │   │   model=AppConfig.OPENAI_MODEL,                                   

    120 │   │   messages=[{"role": "user", "content": prompt}]                  

    121 │   )                                                                   

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_utils/_utils.py:28  

  7 in wrapper                                                                  

                                                                                

    284 │   │   │   │   │   else:                                               

    285 │   │   │   │   │   │   msg = f"Missing required argument: {quote(miss  

    286 │   │   │   │   raise TypeError(msg)                                    

  ❱ 287 │   │   │   return func(*args, **kwargs)                                

    288 │   │                                                                   

    289 │   │   return wrapper  # type: ignore                                  

    290                                                                         

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/resources/chat/comp  

  letions/completions.py:925 in create                                          

                                                                                

     922 │   │   timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,  

     923 │   ) -> ChatCompletion | Stream[ChatCompletionChunk]:                 

     924 │   │   validate_response_format(response_format)                      

  ❱  925 │   │   return self._post(                                             

     926 │   │   │   "/chat/completions",                                       

     927 │   │   │   body=maybe_transform(                                      

     928 │   │   │   │   {                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:123  

  9 in post                                                                     

                                                                                

    1236 │   │   opts = FinalRequestOptions.construct(                          

    1237 │   │   │   method="post", url=path, json_data=body, files=to_httpx_f  

    1238 │   │   )                                                              

  ❱ 1239 │   │   return cast(ResponseT, self.request(cast_to, opts, stream=str  

    1240 │                                                                      

    1241 │   def patch(                                                         

    1242 │   │   self,                                                          

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:958  

  in request                                                                    

                                                                                

     955 │   │   │   options = self._prepare_options(options)                   

     956 │   │   │                                                              

     957 │   │   │   remaining_retries = max_retries - retries_taken            

  ❱  958 │   │   │   request = self._build_request(options, retries_taken=retr  

     959 │   │   │   self._prepare_request(request)                             

     960 │   │   │                                                              

     961 │   │   │   kwargs: HttpxSendArgs = {}                                 

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:495  

  in _build_request                                                             

                                                                                

     492 │   │   │   else:                                                      

     493 │   │   │   │   raise RuntimeError(f"Unexpected JSON data type, {type  

     494 │   │                                                                  

  ❱  495 │   │   headers = self._build_headers(options, retries_taken=retries_  

     496 │   │   params = _merge_mappings(self.default_query, options.params)   

     497 │   │   content_type = headers.get("Content-Type")                     

     498 │   │   files = options.files                                          

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:439  

  in _build_headers                                                             

                                                                                

     436 │   │   self._validate_headers(headers_dict, custom_headers)           

     437 │   │                                                                  

     438 │   │   # headers are case-insensitive while dictionaries are not.     

  ❱  439 │   │   headers = httpx.Headers(headers_dict)                          

     440 │   │                                                                  

     441 │   │   idempotency_header = self._idempotency_header                  

     442 │   │   if idempotency_header and options.idempotency_key and idempot  

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/httpx/_models.py:156 in     

  __init__                                                                      

                                                                                

     153 │   │   elif isinstance(headers, Mapping):                             

     154 │   │   │   for k, v in headers.items():                               

     155 │   │   │   │   bytes_key = _normalize_header_key(k, encoding)         

  ❱  156 │   │   │   │   bytes_value = _normalize_header_value(v, encoding)     

     157 │   │   │   │   self._list.append((bytes_key, bytes_key.lower(), byte  

     158 │   │   elif headers is not None:                                      

     159 │   │   │   for k, v in headers:                                       

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/httpx/_models.py:82 in      

  _normalize_header_value                                                       

                                                                                

      79 │   │   return value                                                   

      80 │   if not isinstance(value, str):                                     

      81 │   │   raise TypeError(f"Header value must be str or bytes, not {typ  

  ❱   82 │   return value.encode(encoding or "ascii")                           

      83                                                                        

      84                                                                        

      85 def _parse_content_type_charset(content_type: str) -> str | None:      

────────────────────────────────────────────────────────────────────────────────

UnicodeEncodeError: 'ascii' codec can't encode character '\u2026' in position 

10: ordinal not in range(128)

[09:07:19] 🐙 Pulling code changes from Github...

[09:07:20] 📦 Processing dependencies...

[09:07:20] 📦 Processed dependencies!

[09:07:22] 🔄 Updated app!

────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:121 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:640 in code_to_exec                                     

                                                                                

  /mount/src/autointel-ai/app.py:167 in <module>                                

                                                                                

    164 │   │   │   st.write(reviewer.review_code(code_text))                   

    165                                                                         

    166 if __name__ == "__main__":                                              

  ❱ 167 │   main()                                                              

    168                                                                         

                                                                                

  /mount/src/autointel-ai/app.py:143 in main                                    

                                                                                

    140 │   with tabs[1]:                                                       

    141 │   │   q = st.text_input("Ask:")                                       

    142 │   │   if st.button("Ask AI", key="ask"):                              

  ❱ 143 │   │   │   st.write(get_ai_assistant_response(q))                      

    144 │                                                                       

    145 │   with tabs[2]:                                                       

    146 │   │   vin = st.text_input("VIN:")                                     

                                                                                

  /mount/src/autointel-ai/app.py:118 in get_ai_assistant_response               

                                                                                

    115 │   │   return "Prices update often—see Track Listings."                

    116 │   if "mileage" in low:                                                

    117 │   │   return "Lower mileage often means higher value."                

  ❱ 118 │   response = openai.chat.completions.create(                          

    119 │   │   model=AppConfig.OPENAI_MODEL,                                   

    120 │   │   messages=[{"role": "user", "content": prompt}]                  

    121 │   )                                                                   

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_utils/_utils.py:28  

  7 in wrapper                                                                  

                                                                                

    284 │   │   │   │   │   else:                                               

    285 │   │   │   │   │   │   msg = f"Missing required argument: {quote(miss  

    286 │   │   │   │   raise TypeError(msg)                                    

  ❱ 287 │   │   │   return func(*args, **kwargs)                                

    288 │   │                                                                   

    289 │   │   return wrapper  # type: ignore                                  

    290                                                                         

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/resources/chat/comp  

  letions/completions.py:925 in create                                          

                                                                                

     922 │   │   timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,  

     923 │   ) -> ChatCompletion | Stream[ChatCompletionChunk]:                 

     924 │   │   validate_response_format(response_format)                      

  ❱  925 │   │   return self._post(                                             

     926 │   │   │   "/chat/completions",                                       

     927 │   │   │   body=maybe_transform(                                      

     928 │   │   │   │   {                                                      

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:123  

  9 in post                                                                     

                                                                                

    1236 │   │   opts = FinalRequestOptions.construct(                          

    1237 │   │   │   method="post", url=path, json_data=body, files=to_httpx_f  

    1238 │   │   )                                                              

  ❱ 1239 │   │   return cast(ResponseT, self.request(cast_to, opts, stream=str  

    1240 │                                                                      

    1241 │   def patch(                                                         

    1242 │   │   self,                                                          

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:958  

  in request                                                                    

                                                                                

     955 │   │   │   options = self._prepare_options(options)                   

     956 │   │   │                                                              

     957 │   │   │   remaining_retries = max_retries - retries_taken            

  ❱  958 │   │   │   request = self._build_request(options, retries_taken=retr  

     959 │   │   │   self._prepare_request(request)                             

     960 │   │   │                                                              

     961 │   │   │   kwargs: HttpxSendArgs = {}                                 

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:495  

  in _build_request                                                             

                                                                                

     492 │   │   │   else:                                                      

     493 │   │   │   │   raise RuntimeError(f"Unexpected JSON data type, {type  

     494 │   │                                                                  

  ❱  495 │   │   headers = self._build_headers(options, retries_taken=retries_  

     496 │   │   params = _merge_mappings(self.default_query, options.params)   

     497 │   │   content_type = headers.get("Content-Type")                     

     498 │   │   files = options.files                                          

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/openai/_base_client.py:439  

  in _build_headers                                                             

                                                                                

     436 │   │   self._validate_headers(headers_dict, custom_headers)           

     437 │   │                                                                  

     438 │   │   # headers are case-insensitive while dictionaries are not.     

  ❱  439 │   │   headers = httpx.Headers(headers_dict)                          

     440 │   │                                                                  

     441 │   │   idempotency_header = self._idempotency_header                  

     442 │   │   if idempotency_header and options.idempotency_key and idempot  

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/httpx/_models.py:156 in     

  __init__                                                                      

                                                                                

     153 │   │   elif isinstance(headers, Mapping):                             

     154 │   │   │   for k, v in headers.items():                               

     155 │   │   │   │   bytes_key = _normalize_header_key(k, encoding)         

  ❱  156 │   │   │   │   bytes_value = _normalize_header_value(v, encoding)     

     157 │   │   │   │   self._list.append((bytes_key, bytes_key.lower(), byte  

     158 │   │   elif headers is not None:                                      

     159 │   │   │   for k, v in headers:                                       

                                                                                

  /home/adminuser/venv/lib/python3.12/site-packages/httpx/_models.py:82 in      

  _normalize_header_value                                                       

                                                                                

      79 │   │   return value                                                   

      80 │   if not isinstance(value, str):                                     

      81 │   │   raise TypeError(f"Header value must be str or bytes, not {typ  

  ❱   82 │   return value.encode(encoding or "ascii")                           

      83                                                                        

      84                                                                        

      85 def _parse_content_type_charset(content_type: str) -> str | None:      

────────────────────────────────────────────────────────────────────────────────

UnicodeEncodeError: 'ascii' codec can't encode character '\u2026' in position 

10: ordinal not in range(128)

main
