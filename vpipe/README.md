# vpipe Module

This module provides the core pipeline framework for audio and speech processing in the project.  
It includes abstractions for capsules, ports, tasks, queues, mixers, sources, sinks, and service transforms (ASR, TTS, Translation).

## Key Concepts

- **Capsule:** The basic processing unit (e.g., transform, source, sink, mixer).
- **Port:** Connects capsules together, supports chaining and data flow.
- **Task:** Async task runner for background processing.
- **Pipeline/Composite:** Compose multiple capsules into a processing graph.
- **Bus:** Message/event passing between capsules.

## Main Components

- `core/`: Core pipeline abstractions (capsule, port, queue, task, etc.)
- `capsules/audio/`: Audio sources, sinks, mixers, and utilities.
- `capsules/services/`: Service transforms for ASR, TTS, and translation.

## Usage

- Build pipelines by composing capsules and connecting ports.
- Extend by implementing new capsules or service interfaces.
- See `pipelines/` for example pipeline compositions.
