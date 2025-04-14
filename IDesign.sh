#!/bin/bash

# 将项目根目录添加到 PYTHONPATH
export PYTHONPATH="/home/shujie/greatlearning/scene_loop/:$PYTHONPATH"
# 设置基础路径
BASE_DIR="/home/shujie/greatlearning/scene_loop"
IDESIGN_DIR="$BASE_DIR/IDesign"



# 检查是否提供了提示文件
if [ $# -eq 0 ]; then
    PROMPT_FILE="$IDESIGN_DIR/prompt.txt"
    echo "No prompt file specified, using default: $PROMPT_FILE"
elif [ $# -eq 1 ]; then
    PROMPT_FILE=$1
else
    echo "Usage: $0 [prompt_file]"
    echo "If prompt_file is not specified, defaults to 'IDesign/prompt.txt'"
    exit 1
fi

# 检查提示文件是否存在
if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file '$PROMPT_FILE' not found"
    exit 1
fi

# 创建必要的目录
mkdir -p "$IDESIGN_DIR/scene_graph"
mkdir -p "$IDESIGN_DIR/assets"
mkdir -p "$IDESIGN_DIR/results"

# 运行test.py生成场景图
echo "Step 1: Generating scene graphs..."
python "$IDESIGN_DIR/scripts/test.py" "$PROMPT_FILE"

# 每个场景图运行retrieve.py
echo "Step 2: Retrieving assets..."
for scene_graph in "$IDESIGN_DIR/scene_graph"/scene_graph_*.json; do
    if [ -f "$scene_graph" ]; then
        # 从文件名中提取编号
        number=$(basename "$scene_graph" | grep -o '[0-9]\+')
        echo "Processing scene graph $number..."
        
        # 创建资产目录
        asset_dir="$IDESIGN_DIR/assets/scene_$number/"
        mkdir -p "$asset_dir"
        
        # 运行retrieve.py
        python "$IDESIGN_DIR/scripts/retrieve.py" "$scene_graph" "$asset_dir"
    fi
done

# 运行blender脚本生成最终场景
echo "Step 3: Generating 3D scenes..."
for scene_graph in "$IDESIGN_DIR/scene_graph"/scene_graph_*.json; do
    if [ -f "$scene_graph" ]; then
        number=$(basename "$scene_graph" | grep -o '[0-9]\+')
        echo "Generating scene $number..."
        
        # 创建结果目录
        result_dir="$IDESIGN_DIR/results/scene_$number"
        mkdir -p "$result_dir"
        
        # 设置环境变量供blender脚本使用
        export SCENE_NUMBER="$number"
        export SCENE_GRAPH="$scene_graph"
        export ASSET_DIR="$IDESIGN_DIR/assets/scene_$number"
        export OUTPUT_DIR="$result_dir"
        
        # 运行blender
        blender --background --python "$IDESIGN_DIR/scripts/place_in_blender.py"
        
        # 检查结果文件是否生成，使用正确的文件名格式
        if [ -f "$result_dir/scene_$number.blend" ] && [ -f "$result_dir/scene_$number.glb" ]; then
            echo "Success! Scene #$number has been generated:"
            echo "- Scene graph: $scene_graph"
            echo "- Blender file: $result_dir/scene_$number.blend"
            echo "- GLB file: $result_dir/scene_$number.glb"
        else
            echo "Error: Failed to generate scene files for prompt #$number"
        fi
        
        echo "Completed processing scene #$number"
        echo "----------------------------------------"
    fi
done

echo "Workflow completed!"
echo "Results can be found in:"
echo "- Scene graphs: $IDESIGN_DIR/scene_graph/"
echo "- Assets: $IDESIGN_DIR/assets/"
echo "- Final scenes: $IDESIGN_DIR/results/"