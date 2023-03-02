/*
 * xnat-stir-plugin:
 * XNAT http://www.xnat.org
 * Copyright (c) 2022, Physikalisch-Technische Bundesanstalt
 * All Rights Reserved
 *
 * Released under Apache 2.0
 */

package org.nrg.xnat.stir;

import org.nrg.framework.annotations.XnatDataModel;
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.xdat.bean.StirPetlmscandataBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;

@XnatPlugin(value = "stirPlugin", name = "XNAT 1.8 stir plugin",
            dataModels = {@XnatDataModel(value = StirPetlmscandataBean.SCHEMA_ELEMENT_NAME,
                                         singular = "PET listmode data",
                                         plural = "PET listmode data",
                                         code = "STIRLM")})
public class StirXnatPlugin {
}
