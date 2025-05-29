- import openai
+ from openai import OpenAI

…

-def gen_image(desc, temp, city):
-    openai.api_key = os.environ["OPENAI_API_KEY"]
-    res = openai.Image.create(
-        prompt=prompt,
-        n=1,
-        size="1024x1024"
-    )
-    return res["data"][0]["url"]

+def gen_image(desc, temp, city):
+    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+    res = client.images.generate(
+        model="dall-e-3",            # v1系ではモデル名必須
+        prompt=prompt,
+        n=1,
+        size="1024x1024"
+    )
+    return res.data[0].url

