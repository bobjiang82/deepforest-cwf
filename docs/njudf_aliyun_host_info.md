# Host Information: njudf_aliyun

This file records the connection details and console access information for the `njudf_aliyun` host in the `deepforest-cwf` project.

## Server Metadata

- **Host Alias**: `njudf_aliyun`
- **Public IP**: `47.102.84.177`
- **Default SSH User**: `root`
- **System OS**: Ubuntu 24.04 LTS (Kernel: `7.0.0-15-generic #15-Ubuntu SMP PREEMPT_DYNAMIC` / x86_64)

## SSH Configuration Reference

The SSH configuration block is located at `/root/.ssh/config` on the local jump box/environment:

```ssh
Host njudf_aliyun
        HostName 47.102.84.177
        User root
        IdentityFile /root/.ssh/id_rsa
        ProxyCommand connect-proxy -H proxy-dmz.intel.com:912 %h %p
```

### Local Connect Command

To connect to this machine from the workspace terminal, run:

```bash
ssh njudf_aliyun
```

## Aliyun ECS Console Link

- **ECS Console Direct Link**: [Aliyun ECS Console Server Detail](https://ecs.console.aliyun.com/server/i-uf69id29064chnb7opd3/detail?spm=5176.ecscore_server.0.0.55fd4df5PUaBjd&regionId=cn-shanghai#/)
- **Instance ID**: `i-uf69id29064chnb7opd3`
- **Region**: Shanghai (`cn-shanghai`)
