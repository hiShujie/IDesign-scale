import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 直接导入当前目录中的IDesign模块
from IDesign import IDesign

def read_prompts(prompt_file):
    with open(prompt_file, 'r') as f:
        # 过滤掉注释和空行
        prompts = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    return prompts

def process_prompt(prompt, prompt_number):
    print(f"\n=== Processing prompt #{prompt_number} ===")
    print(f"Prompt: {prompt}")
    
    try:
        # 确保输出目录存在
        os.makedirs("/home/shujie/greatlearning/scene_loop/IDesign/scene_graph", exist_ok=True)
        
        print("\nCreating IDesign instance...")
        i_design = IDesign(no_of_objects=10,
                          user_input=prompt,
                          room_dimensions=[4.0, 4.0, 2.5])

        print("\nStep 1: Creating initial design...")
        i_design.create_initial_design()
        
        print("\nStep 2: Correcting design...")
        i_design.correct_design()
        
        print("\nStep 3: Refining design...")
        i_design.refine_design()
        
        print("\nStep 4: Creating object clusters...")
        i_design.create_object_clusters(verbose=True)
        
        print("\nStep 5: Running backtracking algorithm...")
        # 检查是否存在必需的物体
        required_objects = ["kitchen_cabinet_1", "countertop_1"]
        scene_objects = [obj["new_object_id"] for obj in i_design.scene_graph["objects_in_room"]]
        
        missing_objects = [obj for obj in required_objects if obj not in scene_objects]
        if missing_objects:
            print(f"\nWarning: Required objects missing from scene: {missing_objects}")
            print("Proceeding without missing objects...")
        
        # 使用新的max_retries参数
        i_design.backtrack(verbose=True, max_retries=10)
        
        # 检查是否所有物体都被成功放置
        unplaced_objects = []
        for obj in i_design.scene_graph:
            if "position" not in obj and obj["new_object_id"] not in ["south_wall", "north_wall", "east_wall", "west_wall", "ceiling", "middle of the room"]:
                unplaced_objects.append(obj["new_object_id"])
        
        if unplaced_objects:
            print(f"\nWarning: Some objects could not be placed: {unplaced_objects}")
        
        # 使用提示编号来命名输出文件
        output_file = f"scene_graph/scene_graph_{prompt_number - 1}.json"
        print(f"\nSaving scene graph to: {output_file}")
        i_design.to_json(output_file)
        
        print(f"\nSuccessfully completed prompt #{prompt_number}")
        if unplaced_objects:
            print(f"Note: {len(unplaced_objects)} objects were not placed")
        
    except Exception as e:
        print(f"\nError in process_prompt for prompt #{prompt_number}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
        # 不再抛出异常，而是返回False表示处理失败
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage help: python test.py <prompt_file>")
        sys.exit(1)

    prompt_file = sys.argv[1]
    
    try:
        prompts = read_prompts(prompt_file)
        print(f"Found {len(prompts)} prompts to process")
        
        for i, prompt in enumerate(prompts, 1):
            try:
                process_prompt(prompt, i)
            except Exception as e:
                print(f"Error processing prompt #{i}: {e}")
                continue
            
    except Exception as e:
        print(f"Error reading prompts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()