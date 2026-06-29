import os
from PIL import Image, ImageDraw, ImageFont

def draw_workflow():
    # Image size
    width = 2100
    height = 500
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 7 phases details
    phases = [
        {"num": "Phase 1", "title_1": "Baseline", "title_2": "MA-RAG Setup"},
        {"num": "Phase 2", "title_1": "Debater Agent", "title_2": "Integration"},
        {"num": "Phase 3", "title_1": "Guardian Layer", "title_2": "Development"},
        {"num": "Phase 4", "title_1": "SHAP", "title_2": "Explainability"},
        {"num": "Phase 5", "title_1": "RL-Based", "title_2": "Optimization"},
        {"num": "Phase 6", "title_1": "Agent 6", "title_2": "Summarization"},
        {"num": "Phase 7", "title_1": "Evaluation &", "title_2": "Publication"}
    ]

    # Card layout config
    card_w = 230
    card_h = 240
    gap = 60
    start_x = (width - (7 * card_w + 6 * gap)) // 2
    start_y = (height - card_h) // 2

    # Load Clean Fonts
    # Fallback to default if Segoe UI isn't found
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arialbd.ttf"
        
    try:
        font_num = ImageFont.truetype(font_bold_path, 22)
        font_title = ImageFont.truetype(font_path, 20)
    except IOError:
        # If true type fonts fail, use default
        font_num = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # Draw loop
    for i, phase in enumerate(phases):
        x1 = start_x + i * (card_w + gap)
        y1 = start_y
        x2 = x1 + card_w
        y2 = y1 + card_h

        # 1. Draw rounded rectangle for Card Background
        # Light sky-blue background: (240, 249, 255)
        # Border sky-blue: (14, 165, 233)
        draw.rounded_rectangle([x1, y1, x2, y2], radius=15, fill=(240, 249, 255, 255), outline=(14, 165, 233, 255), width=3)

        # 2. Draw text
        # Draw Phase Number
        num_text = phase["num"]
        num_w = draw.textlength(num_text, font=font_num)
        draw.text((x1 + (card_w - num_w)/2, y1 + 35), num_text, fill=(2, 132, 199, 255), font=font_num)

        # Draw Line Separator
        draw.line([x1 + 30, y1 + 80, x2 - 30, y1 + 80], fill=(224, 242, 254, 255), width=2)

        # Draw Title Line 1
        t1 = phase["title_1"]
        t1_w = draw.textlength(t1, font=font_title)
        draw.text((x1 + (card_w - t1_w)/2, y1 + 105), t1, fill=(15, 23, 42, 255), font=font_title)

        # Draw Title Line 2
        t2 = phase["title_2"]
        t2_w = draw.textlength(t2, font=font_title)
        draw.text((x1 + (card_w - t2_w)/2, y1 + 145), t2, fill=(15, 23, 42, 255), font=font_title)

        # 3. Draw Connecting Arrow to Next Card
        if i < 6:
            arrow_start_x = x2 + 5
            arrow_end_x = x2 + gap - 5
            arrow_y = y1 + card_h // 2
            
            # Draw line
            draw.line([arrow_start_x, arrow_y, arrow_end_x - 10, arrow_y], fill=(100, 116, 139, 255), width=4)
            # Draw arrowhead polygon
            draw.polygon([
                (arrow_end_x, arrow_y),
                (arrow_end_x - 12, arrow_y - 8),
                (arrow_end_x - 12, arrow_y + 8)
            ], fill=(100, 116, 139, 255))

    # Save image
    output_path = r"c:\Users\Suhas Sreenath\Desktop\Medical_Hallucination_Aware_RAG\MA-RAG\workflow.png"
    img.save(output_path)
    print(f"Successfully generated workflow diagram at: {output_path}")

if __name__ == "__main__":
    draw_workflow()
