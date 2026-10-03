package local.manametalspiritual;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.SidedProxy;
import cpw.mods.fml.common.event.FMLInitializationEvent;

@Mod(modid = SpiritualAutoReset.MOD_ID, name = "ManaMetal Spiritual Auto Reset",
        version = "1.1.0", acceptedMinecraftVersions = "[1.7.10]",
        dependencies = "required-after:manametalmod", acceptableRemoteVersions = "*")
public final class SpiritualAutoReset {
    public static final String MOD_ID = "manametalspiritualautoreset";

    @SidedProxy(clientSide = "local.manametalspiritual.ClientProxy",
            serverSide = "local.manametalspiritual.CommonProxy")
    public static CommonProxy proxy;

    @Mod.EventHandler
    public void init(FMLInitializationEvent event) { proxy.init(); }
}
