def build_marketing_prompt(raw_prompt: str, ad_style: str) -> str:
    """
    自动补全渲染词，将营销人员输入的简短文本转化为专业广告级图片描述
    """
    style_modifiers = {
        "Commercial Studio (商业摄影)": "hyper-realistic commercial product photography, professional studio lighting, 8k resolution, clean background, sharp focus, vibrant colors",
        "3D Tech Render (3D 科技感)": "modern 3D render, Octane render style, minimalist, futuristic lighting, soft shadows, sleek material textures",
        "Minimalist Banner (极简海报)": "minimalist aesthetic, elegant design, soft natural lighting, pastel tone, high-end commercial style",
        "Cinematic Lifestyle (生活场景)": "cinematic lighting, warm atmosphere, authentic human moment, depth of field, 35mm photograph"
    }
    
    modifier = style_modifiers.get(ad_style, style_modifiers["Commercial Studio (商业摄影)"])
    return f"{modifier}. Subject: {raw_prompt}"
