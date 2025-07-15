locals {
  infoblox_ami_id  = "ami-08659b5070b66249d" # NIOS-X AMI ID
  join_token       = var.infoblox_join_token
}

# LAN1 NIC (used for MGMT + LAN)
resource "aws_network_interface" "gm_lan1" {
  subnet_id       = aws_subnet.public.id
  private_ips     = ["10.100.0.200"]
  security_groups = [aws_security_group.rdp_sg.id]

  tags = {
    Name = "gm-lan1-nic"
  }
}

# GM EC2 Instance
resource "aws_instance" "gm" {
  ami           = local.infoblox_ami_id
  instance_type = "m5.2xlarge"
  key_name      = aws_key_pair.rdp.key_name

  network_interface {
    network_interface_id = aws_network_interface.gm_lan1.id
    device_index         = 0
  }

  user_data = <<-EOF
    #cloud-config
    host_setup:
      jointoken: "${local.join_token}"
  EOF

  metadata_options {
    http_tokens              = "optional"
    http_put_response_hop_limit = 1
    http_endpoint            = "enabled"
    instance_metadata_tags   = "enabled"
  }

  tags = {
    Name = "Infoblox-GM"
  }

  depends_on = [aws_internet_gateway.gw]
}

# EIP for LAN1 (public access to GM)
resource "aws_eip" "gm_eip" {
  domain = "vpc"

  tags = {
    Name = "gm-eip-lan1"
  }
}

resource "aws_eip_association" "gm_eip_assoc_lan1" {
  network_interface_id = aws_network_interface.gm_lan1.id
  allocation_id        = aws_eip.gm_eip.id
  private_ip_address   = "10.100.0.200"
}
