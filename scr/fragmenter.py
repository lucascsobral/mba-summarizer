import subprocess
import os

"""
    OBS:
    Usei a bibliteca subprocess para chamar o ffmpeg, no lugar de instalar a biblioteca ffmpeg-python. Apenas para
    otimizar o tempo de download e instalação de dependências, já que baixei para transformar o vídeo em áudio wav.
"""

def fragment_audio(input_file, output_folder, segment_duration=150):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        command = [
            'ffmpeg',
            '-i', input_file,  # input file
            '-f', 'segment',  # specify segmenting mode
            '-segment_time', str(segment_duration),  # segment time in seconds
            '-c', 'copy',  # copy the codec, no re-encoding
            os.path.join(output_folder, 'output%03d.wav')  # output files
        ]

        subprocess.run(command)
        return True
    except Exception as e:
        print(f"Erro ao fragmentar o áudio: {e}")
        return False