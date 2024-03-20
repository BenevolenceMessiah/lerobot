def make_policy(cfg):
    if cfg.policy.name != "diffusion" and cfg.rollout_batch_size > 1:
        raise NotImplementedError("Only diffusion policy supports rollout_batch_size > 1 for the time being.")

    if cfg.policy.name == "tdmpc":
        from lerobot.common.policies.tdmpc.policy import TDMPC

        policy = TDMPC(cfg.policy, cfg.device)
    elif cfg.policy.name == "diffusion":
        from lerobot.common.policies.diffusion.policy import DiffusionPolicy

        policy = DiffusionPolicy(
            cfg=cfg.policy,
            cfg_device=cfg.device,
            cfg_noise_scheduler=cfg.noise_scheduler,
            cfg_rgb_model=cfg.rgb_model,
            cfg_obs_encoder=cfg.obs_encoder,
            cfg_optimizer=cfg.optimizer,
            cfg_ema=cfg.ema,
            n_action_steps=cfg.n_action_steps + cfg.n_latency_steps,
            **cfg.policy,
        )
    elif cfg.policy.name == "act":
        from lerobot.common.policies.act.policy import ActionChunkingTransformerPolicy

        policy = ActionChunkingTransformerPolicy(
            cfg.policy, cfg.device, n_action_steps=cfg.n_action_steps + cfg.n_latency_steps
        )
    else:
        raise ValueError(cfg.policy.name)

    if cfg.policy.pretrained_model_path:
        # TODO(rcadene): hack for old pretrained models from fowm
        if cfg.policy.name == "tdmpc" and "fowm" in cfg.policy.pretrained_model_path:
            if "offline" in cfg.pretrained_model_path:
                policy.step[0] = 25000
            elif "final" in cfg.pretrained_model_path:
                policy.step[0] = 100000
            else:
                raise NotImplementedError()
        policy.load(cfg.policy.pretrained_model_path)

    # import torch
    # loaded = torch.load('/home/alexander/Downloads/dp_ema.pth')
    # aligned = {}

    # their_prefix = "obs_encoder.obs_nets.image.backbone"
    # our_prefix = "obs_encoder.key_model_map.image.backbone"
    # aligned.update({our_prefix + k.removeprefix(their_prefix): v for k, v in loaded.items() if k.startswith(their_prefix)})
    # their_prefix = "obs_encoder.obs_nets.image.pool"
    # our_prefix = "obs_encoder.key_model_map.image.pool"
    # aligned.update({our_prefix + k.removeprefix(their_prefix): v for k, v in loaded.items() if k.startswith(their_prefix)})
    # their_prefix = "obs_encoder.obs_nets.image.nets.3"
    # our_prefix = "obs_encoder.key_model_map.image.out"
    # aligned.update({our_prefix + k.removeprefix(their_prefix): v for k, v in loaded.items() if k.startswith(their_prefix)})

    # aligned.update({k: v for k, v in loaded.items() if k.startswith('model.')})
    # missing_keys, unexpected_keys = policy.diffusion.load_state_dict(aligned, strict=False)
    # assert all('_dummy_variable' in k for k in missing_keys)
    # assert len(unexpected_keys) == 0

    return policy
