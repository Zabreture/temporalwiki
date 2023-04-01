from lightning.pytorch.utilities.deepspeed import convert_zero_checkpoint_to_fp32_state_dict
import os
# lightning deepspeed has saved a directory instead of a file

##### Please modify this part #####
checkpoint_dir = 'outputs/GPT2_large_12_1e-4_diff_lora'
output_path = 'outputs/GPT2_large_12_1e-4_diff_lora_/'

if not os.path.isdir(output_path):
    os.mkdir(output_path)

lst = os.listdir(checkpoint_dir)

for l in lst:
    file = checkpoint_dir+'/'+l
    out = output_path + (l.split('-'))[0]
    convert_zero_checkpoint_to_fp32_state_dict(file, out)
