def build_marketing_prompt(raw_prompt: str, ad_style: str) -> str:
    style_modifiers = {
        "Commercial Studio Photography": "hyper-realistic commercial dental product photography, professional studio light setup, 8k resolution, crisp clean background, ultra-sharp focus, bright natural lighting",
        "3D Render & Aesthetic Micro-Shot": "modern 3D dental render, Octane render engine, crystal clear transparent aesthetic, minimalist studio lighting, sleek glossy material texture",
        "Minimalist Medical & Beauty Banner": "minimalist high-end dental aesthetic, clean soft pastel gradient background, elegant studio setup, premium wellness feel",
        "Cinematic Lifestyle & Smile Shot": "cinematic natural daylight, confident aesthetic smile, depth of field, 35mm portrait photography, authentic human connection"
    }
    
    modifier = style_modifiers.get(ad_style, style_modifiers["Commercial Studio Photography"])
    return f"{modifier}. Subject: {raw_prompt}"
